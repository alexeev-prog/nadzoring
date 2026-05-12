"""Web category connectors: HTTP/HTTPS endpoints and webhooks."""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig


@dataclass
class HttpEndpointConnector(ConnectorBase):
    """Check reachability and response code of an HTTP/HTTPS URL.

    Attributes:
        target: Full URL to probe (e.g. ``"https://example.com/health"``).
        expected_status: HTTP status code considered healthy. Defaults to 200.
        timeout_config: Timeout settings. Defaults to :class:`TimeoutConfig`.
    """

    meta = ConnectorMeta(
        name="http-endpoint",
        category=ConnectorCategory.WEB,
        description="Checks reachability of an HTTP/HTTPS endpoint.",
        tags=("http", "https", "web"),
    )

    target: str
    expected_status: int = 200
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """Send a GET request and verify the response status.

        Returns:
            :class:`ProbeResult` with HTTP status code in ``details``.
        """
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                self.target,
                timeout=self.timeout_config.read,
            ) as response:
                latency_ms = (time.perf_counter() - start) * 1000
                status = response.status
                if status == self.expected_status:
                    return ProbeResult(
                        status="ok",
                        latency_ms=latency_ms,
                        details={"http_status": status},
                    )
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Unexpected HTTP status {status}",
                    details={"http_status": status},
                )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Connection timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))


@dataclass
class WebhookConnector(ConnectorBase):
    """Deliver a POST payload to a webhook URL and verify the response.

    Attributes:
        target: Webhook URL.
        payload: JSON-serialisable body to POST.
        expected_status: HTTP status considered a successful delivery.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="webhook",
        category=ConnectorCategory.WEB,
        description="Posts a payload to a webhook and checks the response.",
        tags=("http", "webhook", "web"),
    )

    target: str
    payload: bytes = b"{}"
    expected_status: int = 200
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """POST the payload to the webhook URL.

        Returns:
            :class:`ProbeResult` with delivery status in ``details``.
        """
        request = urllib.request.Request(
            self.target,
            data=self.payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_config.read,
            ) as response:
                latency_ms = (time.perf_counter() - start) * 1000
                status = response.status
                if status == self.expected_status:
                    return ProbeResult(
                        status="ok",
                        latency_ms=latency_ms,
                        details={"http_status": status},
                    )
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Unexpected delivery status {status}",
                    details={"http_status": status},
                )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Delivery timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))
