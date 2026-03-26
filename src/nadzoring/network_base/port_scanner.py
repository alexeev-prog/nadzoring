"""TCP/UDP port scanning functionality with multi-threading support."""

import socket
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from ipaddress import ip_address
from logging import Logger
from typing import Literal

from nadzoring.logger import get_logger
from nadzoring.network_base.base import DEFAULT_TIMEOUT, HTTP_PORTS
from nadzoring.network_base.service_on_port import get_service_on_port

logger: Logger = get_logger(__name__)

COMMON_PORTS: list[int] = [
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    111,
    135,
    139,
    143,
    443,
    445,
    993,
    995,
    1723,
    3306,
    3389,
    5900,
    8080,
    8443,
    8888,
    9090,
    9200,
    27017,
    27018,
    27019,
    5000,
    5001,
    5005,
    5006,
    5007,
    5008,
    5009,
    5010,
    5432,
    6379,
    11211,
    28017,
]

ScanMode = Literal["fast", "full", "custom"]


@dataclass
class ScanConfig:
    """Configuration for a port scan operation."""

    targets: list[str]
    mode: ScanMode = "fast"
    protocol: Literal["tcp", "udp"] = "tcp"
    custom_ports: list[int] | None = None
    port_range: tuple[int, int] | None = None
    timeout: float = 2.0
    max_workers: int = 50
    grab_banner: bool = True
    progress_callback: Callable[[str, int, int], None] | None = None


@dataclass
class PortResult:
    """Result of a single port scan."""

    port: int
    state: Literal["open", "closed", "filtered", "open|filtered"]
    service: str = "unknown"
    banner: str | None = None
    response_time: float | None = None


@dataclass
class ScanResult:
    """Complete scan result for a single target."""

    target: str
    target_ip: str
    start_time: datetime
    end_time: datetime
    results: dict[int, PortResult] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Calculate scan duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def open_ports(self) -> list[int]:
        """Get list of open port numbers."""
        return [port for port, res in self.results.items() if res.state == "open"]


def resolve_target(target: str) -> str | None:
    """Resolve hostname to IP address."""
    try:
        ip_address(target)
    except ValueError:
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            logger.exception("Failed to resolve hostname: %s", target)
            return None
    else:
        return target


def get_ports_from_mode(config: ScanConfig) -> list[int]:
    """Generate list of ports to scan based on configuration mode."""
    if config.mode == "fast":
        return sorted(COMMON_PORTS)

    if config.mode == "full":
        return list(range(1, 65536))

    if config.mode == "custom":
        if config.custom_ports:
            return sorted(set(config.custom_ports))
        if config.port_range:
            start, end = config.port_range
            return list(range(max(1, start), min(65536, end + 1)))

    return []


def _grab_banner(sock: socket.socket, target_ip: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> str | None:
    """Attempt to grab banner from open port."""
    try:
        sock.settimeout(timeout)
        if port in HTTP_PORTS:
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        elif port == 21:
            sock.send(b"HELP\r\n")
        elif port == 25:
            sock.send(b"EHLO scan.local\r\n")
        elif port == 22:
            pass
        else:
            sock.send(b"\r\n")

        banner: str = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        return banner[:200] if banner else None
    except Exception:
        logger.debug("Banner grab failed for %s:%d", target_ip, port)
        return None


def _scan_tcp_port(
    target_ip: str, port: int, timeout: float = DEFAULT_TIMEOUT, *, grab_banner: bool
) -> tuple[int, PortResult]:
    """Scan a single TCP port on a target."""
    result = PortResult(port=port, state="filtered", service="unknown")
    sock = None

    try:
        start_time: datetime = datetime.now(tz=UTC)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        connection_result: int = sock.connect_ex((target_ip, port))
        response_time: float = (datetime.now(tz=UTC) - start_time).total_seconds() * 1000

        if connection_result == 0:
            result.state = "open"
            result.response_time = round(response_time, 2)
            result.service = get_service_on_port(port)

            if grab_banner:
                banner: str | None = _grab_banner(sock, target_ip, port)
                if banner:
                    result.banner = banner

        elif connection_result in {111, 61}:
            result.state = "closed"
        else:
            result.state = "filtered"

    except TimeoutError:
        result.state = "filtered"
    except Exception as e:
        logger.debug("Error scanning port %d on %s: %s", port, target_ip, e)
        result.state = "filtered"
    finally:
        if sock:
            sock.close()

    return port, result


def _scan_udp_port(target_ip: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> tuple[int, PortResult]:
    """Scan a single UDP port on a target."""
    result = PortResult(port=port, state="filtered", service="unknown")
    sock = None

    try:
        start_time: datetime = datetime.now(tz=UTC)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)

        sock.sendto(b"", (target_ip, port))

        try:
            sock.recvfrom(1024)
            response_time: float = (datetime.now(tz=UTC) - start_time).total_seconds() * 1000
            result.state = "open"
            result.response_time = round(response_time, 2)
            result.service = get_service_on_port(port)
        except TimeoutError:
            result.state = "open|filtered"
        except OSError as e:
            if e.errno == 10054:
                result.state = "closed"

    except Exception as e:
        logger.debug("Error scanning UDP port %d on %s: %s", port, target_ip, e)
    finally:
        if sock:
            sock.close()

    return port, result


def _scan_target_ports(target_ip: str, ports: list[int], config: ScanConfig, target: str) -> ScanResult:
    """Perform port scan on a single target."""
    total_ports: int = len(ports)
    batch_size: int = config.max_workers
    num_batches: int = (total_ports + batch_size - 1) // batch_size

    logger.info(
        "Scanning %s (%s) - %d ports with %d workers",
        target,
        target_ip,
        total_ports,
        batch_size,
    )

    result = ScanResult(
        target=target,
        target_ip=target_ip,
        start_time=datetime.now(tz=UTC),
        end_time=datetime.now(tz=UTC),
        results={},
    )

    completed = 0
    last_update = 0
    update_frequency: int = max(1, total_ports // 100)

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        if config.protocol == "tcp":
            future_to_port: dict[Future[tuple[int, PortResult]], int] = {
                executor.submit(
                    _scan_tcp_port,
                    target_ip,
                    port,
                    config.timeout,
                    grab_banner=config.grab_banner,
                ): port
                for port in ports
            }
        else:
            future_to_port = {
                executor.submit(
                    _scan_udp_port,
                    target_ip,
                    port,
                    config.timeout,
                ): port
                for port in ports
            }

        for future in as_completed(future_to_port):
            port, port_result = future.result()
            result.results[port] = port_result

            completed += 1

            if config.progress_callback and (completed - last_update >= update_frequency or completed == total_ports):
                current_batch: int = (completed + batch_size - 1) // batch_size
                config.progress_callback(
                    f"Batch {current_batch}/{num_batches}",
                    completed,
                    total_ports,
                )
                last_update = completed

    result.end_time = datetime.now(tz=UTC)

    if config.progress_callback:
        config.progress_callback("Completed", total_ports, total_ports)

    logger.info(
        "Scan completed for %s: %d open ports found in %.2f seconds",
        target,
        len(result.open_ports),
        result.duration,
    )

    return result


def scan_ports(config: ScanConfig) -> list[ScanResult]:
    """Scan multiple targets for open ports."""
    ports: list[int] = get_ports_from_mode(config)
    if not ports:
        logger.error("No ports to scan. Check your configuration.")
        return []

    logger.info(
        "Starting scan: %d target(s), %d port(s) each",
        len(config.targets),
        len(ports),
    )

    results: list[ScanResult] = []
    for target in config.targets:
        target_ip: str | None = resolve_target(target)
        if not target_ip:
            logger.warning("Skipping target %s: resolution failed", target)
            continue

        result: ScanResult = _scan_target_ports(target_ip, ports, config, target)
        results.append(result)

    return results
