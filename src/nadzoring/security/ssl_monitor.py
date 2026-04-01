"""Continuous SSL certificate monitoring."""

import time
from collections.abc import Callable
from datetime import UTC, datetime
from logging import Logger
from typing import Any

from nadzoring.logger import get_logger
from nadzoring.security.check_website_ssl_cert import check_ssl_certificate
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

AlertCallback = Callable[[str, str], None]


def _default_alert(domain: str, message: str) -> None:
    """
    Log an SSL alert at WARNING level.

    Args:
        domain: The domain that triggered the alert.
        message: Human-readable alert description.

    """
    logger.warning("SSL alert for %s: %s", domain, message)


class SSLMonitor:
    """
    Periodic SSL certificate monitor for one or more domains.

    Checks certificates on a fixed interval and fires an alert callback
    whenever a certificate is near expiry, has expired, or has changed
    compared to the previous check.

    Attributes:
        domains: List of domain names being monitored.
        interval: Check interval in seconds.
        days_before: Days before expiry to trigger a warning alert.

    Examples:
        >>> monitor = SSLMonitor(["example.com"], interval=3600, days_before=14)
        >>> monitor.set_alert_callback(lambda d, m: print(f"{d}: {m}"))
        >>> monitor.run_cycles(3)

    """

    def __init__(
        self,
        domains: list[str],
        interval: int = 3600,
        days_before: int = 7,
        timeout_config: TimeoutConfig | None = None,
    ) -> None:
        """
        Initialise the monitor.

        Args:
            domains: List of domain names to monitor.
            interval: Seconds between full check cycles. Defaults to
                ``3600``.
            days_before: Days before expiry to emit a warning alert.
                Defaults to ``7``.
            timeout_config: Unified timeout configuration. If None, uses default.

        """
        self.domains: list[str] = domains
        self.interval: int = interval
        self.days_before: int = days_before
        self.timeout_config: TimeoutConfig = timeout_config or TimeoutConfig()

        self._alert_callback: AlertCallback = _default_alert
        self._history: list[dict[str, Any]] = []
        self._previous: dict[str, dict[str, Any]] = {}

    def set_alert_callback(self, callback: AlertCallback) -> None:
        """
        Replace the default alert handler.

        Args:
            callback: Callable accepting ``(domain: str, message: str)``.

        """
        self._alert_callback = callback

    def history(self) -> list[dict[str, Any]]:
        """
        Return all check results accumulated so far.

        Returns:
            List of result dictionaries, each as returned by
            :func:`~nadzoring.security.check_website_ssl_cert.check_ssl_certificate`,
            augmented with a ``checked_at`` ISO timestamp.

        """
        return list(self._history)

    def _check_domain(self, domain: str) -> dict[str, Any]:
        """
        Check a single domain and fire alerts if warranted.

        Args:
            domain: The domain to check.

        Returns:
            Result dictionary from :func:`check_ssl_certificate` with an
            added ``checked_at`` field.

        """
        result: dict[str, Any] = check_ssl_certificate(
            domain,
            self.days_before,
            timeout_config=self.timeout_config,
        )
        result["checked_at"] = datetime.now(tz=UTC).isoformat()

        status: str = result.get("status", "unknown")
        remaining: int | None = result.get("remaining_days")

        if status == "error":
            error_msg: str = result.get("error", "unknown error")
            self._alert_callback(domain, f"Check failed: {error_msg}")
        elif status == "expired":
            self._alert_callback(domain, "Certificate has EXPIRED")
        elif status == "warning" and remaining is not None:
            self._alert_callback(
                domain,
                f"Certificate expires in {remaining} day(s)",
            )

        prev: dict[str, Any] | None = self._previous.get(domain)
        if prev is not None:
            prev_expiry: str | None = prev.get("expiry_date")
            curr_expiry: str | None = result.get("expiry_date")
            if prev_expiry and curr_expiry and prev_expiry != curr_expiry:
                self._alert_callback(
                    domain,
                    f"Certificate changed: expiry {prev_expiry} → {curr_expiry}",
                )

        self._previous[domain] = result
        self._history.append(result)
        return result

    def _run_cycle(self) -> list[dict[str, Any]]:
        """
        Execute one full check cycle across all domains.

        Returns:
            List of result dictionaries for this cycle.

        """
        cycle_results: list[dict[str, Any]] = []
        for domain in self.domains:
            try:
                result: dict[str, Any] = self._check_domain(domain)
                cycle_results.append(result)
            except Exception:
                logger.exception("Unexpected error checking %s", domain)
        return cycle_results

    def run_cycles(self, cycles: int) -> list[dict[str, Any]]:
        """
        Run a fixed number of check cycles, sleeping between them.

        Args:
            cycles: Number of check cycles to execute.

        Returns:
            All result dictionaries produced across all cycles.

        """
        all_results: list[dict[str, Any]] = []
        for i in range(cycles):
            all_results.extend(self._run_cycle())
            if i < cycles - 1:
                time.sleep(self.interval)
        return all_results

    def run(self) -> None:
        """
        Run the monitor indefinitely, sleeping between cycles.

        Intended to be interrupted via :exc:`KeyboardInterrupt`.
        Accumulates results in :meth:`history`.
        """
        while True:
            self._run_cycle()
            time.sleep(self.interval)
