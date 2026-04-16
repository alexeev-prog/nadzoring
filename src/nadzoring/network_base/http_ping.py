"""HTTP/HTTPS response timing and diagnostics."""

import socket
import time
from dataclasses import dataclass, field
from urllib.parse import ParseResult, urlparse

from requests import Session
from requests.exceptions import RequestException

from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig, timeout_context


@dataclass
class HttpPingResult:
    """Result of a single HTTP ping operation."""

    url: str
    final_url: str | None
    status_code: int | None
    dns_ms: float | None
    ttfb_ms: float | None
    total_ms: float | None
    content_length: int | None
    headers: dict[str, str] = field(default_factory=dict)
    error: str | None = None


def _measure_dns(hostname: str) -> float | None:
    """
    Measure DNS resolution time in milliseconds.

    Args:
        hostname: Hostname to resolve.

    Returns:
        Resolution time in milliseconds, or None if resolution failed.

    """
    start: float = time.perf_counter()
    try:
        socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
    return round((time.perf_counter() - start) * 1000, 2)


def http_ping(
    url: str,
    timeout_config: TimeoutConfig | None = None,
    *,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    include_headers: bool = True,
) -> HttpPingResult:
    """
    Perform an HTTP request and collect detailed timing metrics.

    Measures DNS resolution time separately, then tracks time-to-first-byte
    (TTFB) and total download duration using streaming response mode.

    Args:
        url: Target URL to probe. HTTP scheme is added if missing.
        timeout_config: Unified timeout config. If is ``None``, set default timeouts.
        verify_ssl: Whether to verify SSL certificates. Defaults to True.
        follow_redirects: Whether to follow HTTP redirects. Defaults to True.
        include_headers: Whether to include response headers. Defaults to True.

    Returns:
        HttpPingResult with timing breakdown and response metadata.

    Examples:
        >>> result = http_ping("https://example.com")
        >>> result.status_code
        200

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"

    parsed: ParseResult = urlparse(url)
    hostname: str = parsed.hostname or ""

    dns_ms: float | None = _measure_dns(hostname) if hostname else None

    session = Session()
    try:
        start: float = time.perf_counter()
        try:
            with (
                timeout_context(timeout_config),
                session.get(
                    url,
                    stream=True,
                    timeout=(timeout_config.connect, timeout_config.read),
                    verify=verify_ssl,
                    allow_redirects=follow_redirects,
                ) as response,
            ):
                ttfb_ms: float = round((time.perf_counter() - start) * 1000, 2)
                content: bytes = response.content
                total_ms: float = round((time.perf_counter() - start) * 1000, 2)
        except OperationTimeoutError as exc:
            return HttpPingResult(
                url=url,
                final_url=None,
                status_code=None,
                dns_ms=dns_ms,
                ttfb_ms=None,
                total_ms=None,
                content_length=None,
                error=str(exc),
            )

        headers: dict[str, str] = dict(response.headers) if include_headers else {}
        final = str(response.url)

        return HttpPingResult(
            url=url,
            final_url=final if final != url else None,
            status_code=response.status_code,
            dns_ms=dns_ms,
            ttfb_ms=ttfb_ms,
            total_ms=total_ms,
            content_length=len(content),
            headers=headers,
        )
    except RequestException as exc:
        return HttpPingResult(
            url=url,
            final_url=None,
            status_code=None,
            dns_ms=dns_ms,
            ttfb_ms=None,
            total_ms=None,
            content_length=None,
            error=str(exc),
        )
    finally:
        session.close()
