"""Subdomain discovery via certificate transparency logs and DNS brute-force."""

import operator
import socket
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from pathlib import Path
from typing import Any

import requests
from requests import RequestException

from nadzoring.logger import get_logger
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

_CRTSH_URL: str = "https://crt.sh/?q=%.{domain}&output=json"

_DEFAULT_WORDLIST: tuple[str, ...] = (
    "www",
    "mail",
    "ftp",
    "smtp",
    "pop",
    "imap",
    "webmail",
    "admin",
    "portal",
    "api",
    "app",
    "dev",
    "staging",
    "test",
    "beta",
    "vpn",
    "remote",
    "cdn",
    "static",
    "assets",
    "media",
    "images",
    "docs",
    "help",
    "support",
    "forum",
    "blog",
    "shop",
    "store",
    "secure",
    "login",
    "auth",
    "sso",
    "mx",
    "ns",
    "ns1",
    "ns2",
    "dns",
    "gateway",
    "proxy",
    "lb",
    "waf",
    "monitor",
    "status",
    "dashboard",
    "intranet",
    "internal",
    "corp",
    "extranet",
    "git",
    "gitlab",
    "github",
    "jira",
    "confluence",
    "wiki",
    "jenkins",
    "ci",
    "cd",
    "docker",
    "k8s",
    "kubernetes",
    "grafana",
    "kibana",
    "elastic",
    "redis",
    "db",
    "database",
    "mysql",
    "postgres",
    "mongo",
    "backup",
    "files",
    "upload",
    "download",
    "mobile",
    "m",
    "wap",
    "cpanel",
    "whm",
    "plesk",
    "autodiscover",
    "autoconfig",
    "exchange",
    "owa",
)


def _fetch_ct_subdomains(domain: str, timeout_config: TimeoutConfig) -> set[str]:
    """
    Query crt.sh certificate transparency logs for subdomains.

    Args:
        domain: The apex domain to search.
        timeout_config: Unified timeout configuration.
        proxy: Optional proxy URL.

    Returns:
        Set of unique subdomain strings discovered via CT logs.

    """
    url: str = _CRTSH_URL.format(domain=domain)
    subdomains: set[str] = set()

    try:
        response = requests.get(url, timeout=(timeout_config.connect, timeout_config.read))
        response.raise_for_status()
        entries: list[dict[str, Any]] = response.json()

        for entry in entries:
            name: str = entry.get("name_value", "")
            for line in name.splitlines():
                cleaned: str = line.strip().lstrip("*").lstrip(".")
                if cleaned.endswith(domain) and cleaned != domain:
                    subdomains.add(cleaned)
    except (RequestException, ValueError):
        logger.warning("crt.sh query failed for %s", domain)

    return subdomains


def _probe_subdomain(
    subdomain: str,
    timeout_config: TimeoutConfig,
) -> dict[str, Any] | None:
    """
    Attempt to resolve a subdomain and return metadata if it exists.

    Args:
        subdomain: Fully qualified subdomain string to probe.
        timeout_config: Unified timeout configuration.

    Returns:
        Dictionary with ``subdomain`` and ``ip`` keys if the subdomain
        resolves, or ``None`` if it does not.

    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_config.connect)
        sock.connect((subdomain, 80))
        sock.close()
        ip: str = socket.gethostbyname(subdomain)
    except (TimeoutError, socket.gaierror):
        return None
    else:
        return {"subdomain": subdomain, "ip": ip}


def _load_wordlist(path: Path) -> list[str]:
    """
    Read subdomain prefixes from a file.

    Args:
        path: Path to a plain-text wordlist file with one prefix per line.

    Returns:
        List of non-empty, stripped prefix strings.

    """
    try:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        logger.exception("Failed to read wordlist: %s", path)
        return []


def scan_subdomains(
    domain: str,
    *,
    wordlist_path: str | None = None,
    max_threads: int = 20,
    timeout_config: TimeoutConfig | None = None,
) -> list[dict[str, Any]]:
    """
    Discover subdomains using CT logs and optional DNS brute-force.

    First queries certificate transparency logs via crt.sh to collect
    known subdomains, then optionally performs DNS brute-force using a
    wordlist. All candidates are resolved concurrently.

    Args:
        domain: The apex domain to scan (e.g. ``"example.com"``).
        wordlist_path: Path to a custom wordlist file. When ``None``, the
            built-in default wordlist is used for brute-force. Pass an
            empty string to skip brute-force entirely.
        max_threads: Maximum number of concurrent DNS resolution threads.
            Defaults to ``20``.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        List of dictionaries for each discovered live subdomain, each
        containing:

        - ``subdomain`` (str): The fully qualified subdomain.
        - ``ip`` (str): The resolved IPv4/IPv6 address.
        - ``source`` (str): Either ``"ct_log"`` or ``"brute_force"``.

    Examples:
        >>> results = scan_subdomains("example.com", max_threads=10)
        >>> for r in results:
        ...     print(r["subdomain"], r["ip"])

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    ct_subdomains: set[str] = _fetch_ct_subdomains(domain, timeout_config)

    if not wordlist_path:
        brute_candidates: set[str] = set()
    elif wordlist_path is not None:
        prefixes: list[str] = _load_wordlist(Path(wordlist_path))
        brute_candidates = {f"{p}.{domain}" for p in prefixes}
    else:
        brute_candidates = {f"{p}.{domain}" for p in _DEFAULT_WORDLIST}

    source_map: dict[str, str] = {}
    all_candidates: set[str] = set()

    for sub in ct_subdomains:
        source_map[sub] = "ct_log"
        all_candidates.add(sub)

    for sub in brute_candidates:
        if sub not in source_map:
            source_map[sub] = "brute_force"
        all_candidates.add(sub)

    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_sub: dict[Future[dict[str, Any] | None], str] = {
            executor.submit(_probe_subdomain, sub, timeout_config): sub for sub in all_candidates
        }
        for future in as_completed(future_to_sub):
            sub = future_to_sub[future]
            try:
                result: dict[str, Any] | None = future.result()
            except Exception:
                result = None
            if result is not None:
                result["source"] = source_map.get(sub, "unknown")
                results.append(result)

    results.sort(key=operator.itemgetter("subdomain"))
    return results
