"""Active service detection by connecting to a port and analyzing the banner."""

import socket
from dataclasses import dataclass
from logging import Logger
from typing import Literal

from nadzoring.logger import get_logger
from nadzoring.network_base.service_on_port import get_service_on_port
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

SERVICE_SIGNATURES: dict[str, list[bytes]] = {
    "SSH": [b"SSH-", b"OpenSSH"],
    "HTTP": [b"HTTP/", b"<!DOCTYPE", b"<html"],
    "HTTPS": [b"HTTP/", b"<!DOCTYPE"],
    "SMTP": [b"220 ", b"ESMTP"],
    "POP3": [b"+OK", b"-ERR"],
    "IMAP": [b"* OK", b"IMAP"],
    "FTP": [b"220 ", b"FTP"],
    "MySQL": [b"mysql", b"MariaDB"],
    "PostgreSQL": [b"PostgreSQL"],
    "Redis": [b"+OK", b"-ERR", b"redis"],
    "MongoDB": [b"mongodb"],
    "Telnet": [b"Telnet", b"login:"],
}


@dataclass
class ServiceDetectionResult:
    """
    Result of active service detection on a specific port.

    Attributes:
        port: The port number that was scanned
        detected_service: The service identified through banner analysis, if any
        guessed_service: The service guessed from port number using getservbyport
        banner: The banner text received from the service (truncated to 200 chars)
        method: The method used for detection ('banner', 'static', or 'failed')
        error: Error message if detection failed, None otherwise

    """

    port: int
    detected_service: str | None
    guessed_service: str
    banner: str | None
    method: Literal["banner", "static", "failed"]
    error: str | None = None


def detect_service_on_host(
    host: str,
    port: int,
    *,
    timeout_config: TimeoutConfig | None = None,
    send_probe: bool = True,
) -> ServiceDetectionResult:
    """
    Connect to a specific host and port to detect the actual running service.

    Performs active service detection by establishing a TCP connection to the
    specified host and port, optionally sending a protocol-specific probe, and
    analyzing the received banner against known service signatures.

    The detection process follows these steps:
    1. Static service guess using getservbyport (fallback)
    2. TCP connection attempt to the target host and port
    3. Optional protocol-specific probe transmission
    4. Banner reception and analysis against predefined signatures
    5. Fallback to port-based guess if banner analysis fails

    Args:
        host: Target hostname or IP address to scan
        port: Port number to connect to for service detection
        timeout_config: Unified timeout configuration.
        send_probe: Whether to send a protocol-specific probe string
                   (e.g., "HEAD /" for HTTP) to elicit a banner response

    Returns:
        ServiceDetectionResult object containing:
        - detected_service: Service identified via banner analysis (if successful)
        - guessed_service: Service guessed from port number
        - banner: Received banner text (truncated)
        - method: Detection method used
        - error: Error details if connection failed

    Example:
        >>> result = detect_service_on_host("example.com", 80)
        >>> print(result.detected_service)  # "HTTP"
        >>> print(result.banner)  # "HTTP/1.1 200 OK..."

    Notes:
        - The function handles connection errors gracefully, returning a result
          with method="failed" and an appropriate error message
        - Banner analysis is case-insensitive and supports both string and bytes
          pattern matching
        - Common service signatures are defined in SERVICE_SIGNATURES

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    guessed: str = get_service_on_port(port)

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_config.connect)
        sock.connect((host, port))

        if send_probe:
            probe: bytes | None = _get_probe_for_port(port)
            if probe:
                sock.send(probe)

        banner_data: bytes = sock.recv(1024)
        banner: str = banner_data.decode("utf-8", errors="ignore").strip()

        detected: str | None = _analyze_banner(banner, port)

        return ServiceDetectionResult(
            port=port,
            detected_service=detected,
            guessed_service=guessed,
            banner=banner[:200],
            method="banner",
        )

    except ConnectionRefusedError:
        return ServiceDetectionResult(
            port=port,
            detected_service=None,
            guessed_service=guessed,
            banner=None,
            method="failed",
            error="Connection refused",
        )
    except TimeoutError:
        return ServiceDetectionResult(
            port=port,
            detected_service=None,
            guessed_service=guessed,
            banner=None,
            method="failed",
            error="Connection timeout",
        )
    except Exception as e:
        logger.debug("Service detection failed for %s:%d: %s", host, port, e)
        return ServiceDetectionResult(
            port=port,
            detected_service=None,
            guessed_service=guessed,
            banner=None,
            method="failed",
            error=str(e),
        )
    finally:
        if sock:
            sock.close()


def _get_probe_for_port(port: int) -> bytes | None:
    """
    Return an appropriate protocol probe string for common service ports.

    Probes are designed to elicit a banner response from the service for
    identification purposes. Different services require different probe strings
    to trigger a response.

    Args:
        port: The port number to get a probe for

    Returns:
        Bytes object containing the probe string, or None if no probe is defined
        for the specified port

    Notes:
        - HTTP/HTTPS ports receive a HEAD request
        - FTP receives a HELP command
        - SMTP receives an EHLO command
        - SSH, POP3, and IMAP receive empty probes (connection only)
        - Returns None for ports without defined probes

    """
    probes: dict[int, bytes] = {
        80: b"HEAD / HTTP/1.0\r\n\r\n",
        443: b"HEAD / HTTP/1.0\r\n\r\n",
        8080: b"HEAD / HTTP/1.0\r\n\r\n",
        8443: b"HEAD / HTTP/1.0\r\n\r\n",
        21: b"HELP\r\n",
        25: b"EHLO detect.local\r\n",
        22: b"",
        110: b"",
        143: b"",
    }
    return probes.get(port)


def _analyze_banner(banner: str, port: int) -> str | None:
    """
    Analyze a service banner against known service signatures.

    Performs pattern matching on the received banner to identify the running
    service. First checks against predefined signatures in SERVICE_SIGNATURES,
    then falls back to port-based service mapping.

    Args:
        banner: The banner string received from the service
        port: The port number the banner was received from

    Returns:
        Service name string (e.g., "HTTP", "SSH") if identified,
        None if no match is found

    Notes:
        - Pattern matching is case-insensitive for string patterns
        - Supports both string and bytes pattern matching
        - Common port mappings are used as a fallback when banner analysis fails
        - The function checks all signatures in SERVICE_SIGNATURES in order

    """
    banner_lower: str = banner.lower()
    banner_bytes: bytes = banner.encode()

    for service, signatures in SERVICE_SIGNATURES.items():
        for sig in signatures:
            if isinstance(sig, bytes) and sig in banner_bytes:
                return service
            if isinstance(sig, str) and sig.lower() in banner_lower:
                return service

    port_services: dict[int, str] = {
        80: "HTTP",
        443: "HTTPS",
        22: "SSH",
        21: "FTP",
        25: "SMTP",
    }
    return port_services.get(port)
