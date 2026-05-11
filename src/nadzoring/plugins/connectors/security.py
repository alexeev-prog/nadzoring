"""Security category connectors — wraps every command from ``nadzoring security``."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig

_TAGS = ("security",)


def _ok(data: Any, latency_ms: float | None = None) -> ProbeResult:
    return ProbeResult(status="ok", latency_ms=latency_ms, details={"data": data})


def _err(msg: str) -> ProbeResult:
    return ProbeResult(status="error", error=msg)


# ---------------------------------------------------------------------------
# security check-ssl
# ---------------------------------------------------------------------------


@dataclass
class SslCertConnector(ConnectorBase):
    """Check TLS certificate validity and expiry for domains.

    Wraps :func:`nadzoring.security.check_ssl_certificate_safe`.

    Attributes:
        domains: Domains to check.
        days_before: Warn when certificate expires within this many days.
        verify: Verify certificate chain. Defaults to ``True``.
        full: Return full certificate details instead of summary.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="ssl-cert",
        category=ConnectorCategory.NETWORK,
        description="Checks TLS certificate validity and days until expiry.",
        tags=(*_TAGS, "ssl", "tls"),
    )

    domains: list[str]
    days_before: int = 7
    verify: bool = True
    full: bool = False
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.security.check_website_ssl_cert import (
            check_ssl_certificate_safe,
            check_ssl_expiry_with_fallback,
        )

        results = []
        errors = []
        for domain in self.domains:
            if self.full:
                res = check_ssl_certificate_safe(
                    domain,
                    self.days_before,
                    verify=self.verify,
                    timeout_config=self.timeout_config,
                )
            else:
                res = check_ssl_expiry_with_fallback(
                    domain, self.days_before, self.timeout_config
                )

            if res.get("error"):
                errors.append(f"{domain}: {res['error']}")
            else:
                results.append(res)

        if errors and not results:
            return _err("; ".join(errors))

        # Determine overall status from expiry warnings
        expiring = [
            r for r in results
            if r.get("days_remaining") is not None and r["days_remaining"] <= self.days_before
        ]
        return ProbeResult(
            status="degraded" if expiring or errors else "ok",
            error=(
                f"Expiring soon: {', '.join(r.get('domain', '') for r in expiring)}"
                if expiring
                else ("; ".join(errors) if errors else None)
            ),
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# security check-headers
# ---------------------------------------------------------------------------


@dataclass
class HttpHeadersConnector(ConnectorBase):
    """Analyse HTTP security headers for one or more URLs.

    Wraps :func:`nadzoring.security.http_headers.check_http_security_headers`.

    Attributes:
        urls: URLs to check.
        verify_ssl: Verify TLS certificates. Defaults to ``True``.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="http-headers",
        category=ConnectorCategory.NETWORK,
        description="Checks HTTP security headers (CSP, HSTS, X-Frame-Options…).",
        tags=(*_TAGS, "http", "headers"),
    )

    urls: list[str]
    verify_ssl: bool = True
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.security.http_headers import check_http_security_headers

        results = []
        errors = []
        for url in self.urls:
            res = check_http_security_headers(
                url,
                timeout_config=self.timeout_config,
                verify_ssl=self.verify_ssl,
            )
            if res.get("error"):
                errors.append(f"{url}: {res['error']}")
            else:
                results.append(res)

        if errors and not results:
            return _err("; ".join(errors))

        # Flag any URL with a security score below 50 as degraded
        low_score = [r for r in results if (r.get("score") or 100) < 50]
        return ProbeResult(
            status="degraded" if low_score or errors else "ok",
            error=(
                f"Low security score on: {', '.join(r.get('url', '') for r in low_score)}"
                if low_score
                else ("; ".join(errors) if errors else None)
            ),
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# security check-email
# ---------------------------------------------------------------------------


@dataclass
class EmailSecurityConnector(ConnectorBase):
    """Check SPF, DKIM, and DMARC records for domains.

    Wraps :func:`nadzoring.security.email_security.check_email_security`.

    Attributes:
        domains: Domains to check.
    """

    meta = ConnectorMeta(
        name="email-security",
        category=ConnectorCategory.NETWORK,
        description="Checks SPF, DKIM, and DMARC DNS records.",
        tags=(*_TAGS, "email", "spf", "dkim", "dmarc"),
    )

    domains: list[str]

    def probe(self) -> ProbeResult:
        from nadzoring.security.email_security import check_email_security

        results = []
        errors = []
        for domain in self.domains:
            try:
                data = check_email_security(domain)
                results.append(data)
            except Exception as exc:
                errors.append(f"{domain}: {exc}")

        if errors and not results:
            return _err("; ".join(errors))

        # Flag domains missing SPF or DMARC as degraded
        missing = [
            r.get("domain", "")
            for r in results
            if not r.get("spf", {}).get("found") or not r.get("dmarc", {}).get("found")
        ]
        return ProbeResult(
            status="degraded" if missing or errors else "ok",
            error=(
                f"Missing/invalid SPF or DMARC on: {', '.join(missing)}"
                if missing
                else ("; ".join(errors) if errors else None)
            ),
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# security subdomains
# ---------------------------------------------------------------------------


@dataclass
class SubdomainScanConnector(ConnectorBase):
    """Enumerate subdomains for a domain via CT logs and brute-force.

    Wraps :func:`nadzoring.security.subdomain_scan.scan_subdomains`.

    Attributes:
        domain: Target domain.
        wordlist_path: Path to a custom wordlist file. ``None`` uses the
            built-in list.
        threads: Number of concurrent probe threads. Defaults to 20.
        bruteforce: Enable wordlist brute-forcing in addition to CT logs.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="subdomain-scan",
        category=ConnectorCategory.NETWORK,
        description="Enumerates subdomains via CT logs and optional brute-force.",
        tags=(*_TAGS, "subdomain", "recon"),
    )

    domain: str
    wordlist_path: Path | None = None
    threads: int = 20
    bruteforce: bool = True
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.security.subdomain_scan import scan_subdomains

        try:
            if not self.bruteforce:
                wordlist: str | None = ""
            elif self.wordlist_path is not None:
                wordlist = str(self.wordlist_path)
            else:
                wordlist = None
            results = scan_subdomains(
                self.domain,
                wordlist_path=wordlist,
                max_threads=self.threads,
                timeout_config=self.timeout_config,
            )
            return ProbeResult(
                status="ok",
                details={"data": results, "count": len(results)},
            )
        except Exception as exc:
            return _err(str(exc))
