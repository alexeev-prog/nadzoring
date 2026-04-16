"""HTTP security header analysis."""

from dataclasses import dataclass, field
from logging import Logger
from typing import Any

import requests
from requests import Response

from nadzoring.logger import get_logger
from nadzoring.security.errors import HTTPHeaderError
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

_SECURITY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "hsts",
    "Content-Security-Policy": "csp",
    "X-Content-Type-Options": "x_content_type_options",
    "X-Frame-Options": "x_frame_options",
    "X-XSS-Protection": "x_xss_protection",
    "Referrer-Policy": "referrer_policy",
    "Permissions-Policy": "permissions_policy",
    "Cross-Origin-Embedder-Policy": "coep",
    "Cross-Origin-Opener-Policy": "coop",
    "Cross-Origin-Resource-Policy": "corp",
    "Cache-Control": "cache_control",
}

_DEPRECATED_HEADERS: frozenset[str] = frozenset({
    "X-XSS-Protection",
    "Expect-CT",
})

_LEAK_HEADERS: frozenset[str] = frozenset({
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
    "X-Generator",
})


@dataclass
class HeaderAnalysis:
    """Result of analysing HTTP security headers for a single URL.

    Attributes:
        url: The final (post-redirect) URL that was probed.
        status_code: HTTP response status code, or ``None`` on error.
        present: Mapping of header name to its value for headers that
            were found.
        missing: List of recommended security headers that were absent.
        deprecated: List of deprecated security headers that were present.
        leaking: Mapping of information-leaking header names to their
            values.
        score: Integer score from 0-100 reflecting header coverage.
        error: Error message when the request itself failed.
    """

    url: str
    status_code: int | None = None
    present: dict[str, str] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    deprecated: list[str] = field(default_factory=list)
    leaking: dict[str, str] = field(default_factory=dict)
    score: int = 0
    error: HTTPHeaderError | None = None


def _score_headers(present: dict[str, str], missing: list[str]) -> int:
    """Calculate a simple coverage score for security headers.

    Args:
        present: Headers that were found in the response.
        missing: Recommended headers that were absent (reserved for future
            weighted scoring).

    Returns:
        Integer between 0 and 100 representing the percentage of recommended
        security headers present in the response.
    """
    total: int = len(_SECURITY_HEADERS)
    if total == 0:
        return 0
    return round((len(present) / total) * 100)


def _analyse_response(url: str, response: Response) -> HeaderAnalysis:
    """Parse a ``requests`` response object into a ``HeaderAnalysis``.

    Args:
        url: The original request URL.
        response: The HTTP response to analyse.

    Returns:
        Populated ``HeaderAnalysis`` instance.
    """
    headers_lower: dict[str, str] = {k.lower(): v for k, v in response.headers.items()}

    present: dict[str, str] = {}
    missing: list[str] = []

    for header in _SECURITY_HEADERS:
        value: str | None = headers_lower.get(header.lower())
        if value is not None:
            present[header] = value
        else:
            missing.append(header)

    deprecated: list[str] = [h for h in _DEPRECATED_HEADERS if h.lower() in headers_lower]

    leaking: dict[str, str] = {h: headers_lower[h.lower()] for h in _LEAK_HEADERS if h.lower() in headers_lower}

    score: int = _score_headers(present, missing)

    return HeaderAnalysis(
        url=str(response.url),
        status_code=response.status_code,
        present=present,
        missing=missing,
        deprecated=deprecated,
        leaking=leaking,
        score=score,
    )


def check_http_security_headers(
    url: str,
    *,
    timeout_config: TimeoutConfig | None = None,
    verify_ssl: bool = True,
) -> dict[str, Any]:
    """Analyse HTTP security headers for the given URL.

    Sends a HEAD request (falling back to GET on failure) to the target
    URL and evaluates the response headers against a list of recommended
    security headers.

    The returned dictionary's ``"error"`` field, if present, contains one of
    the literals defined in :data:`nadzoring.security.errors.HTTPHeaderError`.

    Args:
        url: The target URL, with or without scheme. ``http://`` is
            prepended when no scheme is present.
        timeout_config: Unified timeout configuration. If None, uses default.
        verify_ssl: Whether to verify the SSL certificate. Defaults to
            ``True``.

    Returns:
        Dictionary representation of a :class:`HeaderAnalysis` with the
        following keys:

        - ``url`` (str): Final URL after redirects.
        - ``status_code`` (int | None): HTTP status code.
        - ``present`` (dict): Found security headers and their values.
        - ``missing`` (list): Recommended headers that were absent.
        - ``deprecated`` (list): Deprecated headers found in response.
        - ``leaking`` (dict): Information-leaking headers and values.
        - ``score`` (int): Coverage score 0-100.
        - ``error`` (str | None): Error message on request failure.

    Examples:
        >>> result = check_http_security_headers("https://example.com")
        >>> result["score"]
        40
        >>> "Strict-Transport-Security" in result["present"]
        True
    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        response: Response = requests.get(
            url,
            timeout=(timeout_config.connect, timeout_config.read),
            verify=verify_ssl,
            allow_redirects=True,
        )
        analysis: HeaderAnalysis = _analyse_response(url, response)
    except requests.exceptions.Timeout:
        logger.warning("Request timeout for %s", url)
        analysis = HeaderAnalysis(url=url, error="Request timeout")
    except requests.exceptions.ConnectionError:
        logger.warning("Connection refused for %s", url)
        analysis = HeaderAnalysis(url=url, error="Connection refused")
    except requests.exceptions.SSLError:
        logger.warning("SSL verification failed for %s", url)
        analysis = HeaderAnalysis(url=url, error="SSL verification failed")
    except requests.exceptions.TooManyRedirects:
        logger.warning("Too many redirects for %s", url)
        analysis = HeaderAnalysis(url=url, error="Too many redirects")
    except requests.exceptions.RequestException as exc:
        logger.warning("Request failed for %s: %s", url, exc)
        analysis = HeaderAnalysis(url=url, error="Invalid URL")

    return {
        "url": analysis.url,
        "status_code": analysis.status_code,
        "present": analysis.present,
        "missing": analysis.missing,
        "deprecated": analysis.deprecated,
        "leaking": analysis.leaking,
        "score": analysis.score,
        "error": analysis.error,
    }
