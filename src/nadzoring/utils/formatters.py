"""Output formatting utilities for CLI commands."""

import csv
import json
import shutil
from collections.abc import Sequence
from csv import DictWriter
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Literal

import click
from tabulate import tabulate

from nadzoring.network_base.port_scanner import ScanResult

type OutputFormat = Literal["table", "json", "csv", "html", "html_table"]
"""Valid output format types for CLI commands."""

type RecordData = dict[str, Any]
"""Type alias for DNS record data structures."""


def get_terminal_width() -> int:
    """Get the current terminal width in columns.

    Returns:
        int: Number of columns available in the terminal. Falls back to a
            reasonable default if terminal size cannot be determined.
    """
    return shutil.get_terminal_size().columns


def truncate_string(s: str, max_width: int, placeholder: str = "...") -> str:
    """Truncate a string to fit within a specified width.

    If the string exceeds the maximum width, it is truncated and the placeholder
    is appended to indicate truncation.

    Args:
        s: The string to truncate.
        max_width: Maximum allowed width in characters.
        placeholder: String to append when truncated (default: "...").

    Returns:
        str: Original string if within limits, otherwise truncated version
            with placeholder appended.

    Example:
        >>> truncate_string("very long string", 10)
        'very lo...'
    """
    if len(s) <= max_width:
        return s
    return s[: max_width - len(placeholder)] + placeholder


def colorize_value(value: Any, *, no_color: bool = False) -> str:
    """Apply color formatting to values based on content and severity.

    Colors are applied based on keywords in the string value:
        - Red/bold: Critical/high severity terms
        - Yellow/bold: Medium severity/warning terms
        - Green: Low severity/positive terms
        - No color: Other values

    Args:
        value: The value to colorize.
        no_color: If True, disable color formatting (default: False).

    Returns:
        str: Colorized string if colors enabled, otherwise plain string.

    Example:
        >>> colorize_value("CRITICAL")
        '\x1b[1;31mCRITICAL\x1b[0m'  # Red bold text
    """
    if no_color:
        return str(value)

    value_str = str(value)

    if isinstance(value, str):
        if value.upper() in ["CRITICAL", "HIGH", "POISONED", "ERROR", "NXDOMAIN"]:
            return click.style(value_str, fg="red", bold=True)
        if value.upper() in ["MEDIUM", "WARNING", "MISMATCH", "TTL_DIFF"]:
            return click.style(value_str, fg="yellow", bold=True)
        if value.upper() in ["LOW", "INFO", "REFERENCE", "CLEAN"]:
            return click.style(value_str, fg="green")
        if value.lower() in ["yes", "up", "passed", "good", "healthy"]:
            return click.style(value_str, fg="green")

    return value_str


def print_results_table(
    data: Sequence[dict[str, Any]],
    tablefmt: str = "simple_grid",
    *,
    no_color: bool = False,
) -> None:
    """Print results as a formatted table that fits terminal width.

    Automatically adjusts column widths based on terminal size and content.
    Special handling for DNS record types (TXT, AAAA, etc.) with predefined
    maximum widths.

    Args:
        data: List of dictionaries containing the results to display.
        tablefmt: Tabulate table format string (default: "simple_grid").
        no_color: If True, disable color formatting (default: False).

    Returns:
        None: Results are printed directly to console.

    Example:
        >>> data = [{"domain": "example.com", "A": "192.168.1.1"}]
        >>> print_results_table(data)
        +-------------+-------------+
        | domain      | A           |
        +-------------+-------------+
        | example.com | 192.168.1.1 |
        +-------------+-------------+
    """
    if not data:
        click.echo("No results to display")
        return

    if not no_color:
        data = [
            {key: colorize_value(value) for key, value in row.items()} for row in data
        ]

    term_width: int = get_terminal_width()
    headers: list[str] = list(data[0].keys())

    min_widths: dict[str, int] = {h: len(h) for h in headers}
    max_widths: dict[str, int] = dict.fromkeys(headers, 80)

    special_limits: dict[str, int] = {
        "TXT": 60,
        "AAAA": 40,
        "A": 30,
        "MX": 40,
        "NS": 40,
        "SOA": 60,
    }
    for h, w in special_limits.items():
        if h in max_widths:
            max_widths[h] = w

    borders: int = len(headers) * 3 + 1
    available: int = term_width - borders

    if available <= 0:
        widths = [min_widths[h] for h in headers]
    else:
        widths: list[int] = _calculate_column_widths(
            headers, min_widths, max_widths, available
        )

    try:
        output: str = tabulate(
            data,
            headers="keys",
            tablefmt=tablefmt,
            maxcolwidths=widths,
            stralign="left",
            numalign="left",
        )
    except Exception:
        output: str = tabulate(data, headers="keys", tablefmt="simple")

    click.echo(output)


def _calculate_column_widths(
    headers: list[str],
    min_widths: dict[str, int],
    max_widths: dict[str, int],
    available: int,
) -> list[int]:
    """Calculate optimal column widths within available space.

    Distributes extra space proportionally while respecting minimum and
    maximum constraints for each column.

    Args:
        headers: List of column header names.
        min_widths: Dictionary mapping headers to minimum required widths.
        max_widths: Dictionary mapping headers to maximum allowed widths.
        available: Total available width for all columns combined.

    Returns:
        list[int]: Calculated width for each column in header order.
    """
    total_min: Literal[0] | int = sum(min_widths.values())

    if total_min >= available:
        return [min_widths[h] for h in headers]

    extra: float = (available - total_min) / len(headers)
    col_widths: dict[str, int] = {}

    for h in headers:
        new = int(min_widths[h] + extra)
        col_widths[h] = min(new, max_widths[h])

    total: Literal[0] | int = sum(col_widths.values())
    if total <= available:
        return [col_widths[h] for h in headers]

    overflow: int = total - available
    sorted_cols: list[str] = sorted(headers, key=lambda h: col_widths[h], reverse=True)

    for h in sorted_cols:
        if overflow <= 0:
            break
        reduction: int = min(overflow, col_widths[h] - min_widths[h])
        col_widths[h] -= reduction
        overflow -= reduction

    return [col_widths[h] for h in headers]


def print_csv_table(data: Sequence[dict[str, Any]]) -> None:
    """Print data as CSV format to console.

    Args:
        data: List of dictionaries to convert to CSV format. All dictionaries
            should have the same keys for proper CSV formatting.

    Returns:
        None: CSV data is printed directly to console.

    Example:
        >>> data = [{"domain": "example.com", "ip": "192.168.1.1"}]
        >>> print_csv_table(data)
        domain,ip
        example.com,192.168.1.1
    """
    if not data:
        click.echo("No data to display")
        return

    output = StringIO()
    writer: DictWriter[str] = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    click.echo(output.getvalue())


def print_html_table(
    data: Sequence[dict[str, Any]], *, full_page: bool = False
) -> None:
    """Print results as HTML table or complete HTML page.

    Args:
        data: List of dictionaries containing the results to format.
        full_page: If True, generate complete HTML page with styling and
            timestamp. If False, generate only the HTML table (default: False).

    Returns:
        None: HTML content is printed directly to console.

    Example:
        >>> data = [{"domain": "example.com", "status": "OK"}]
        >>> print_html_table(data)
        <table>...
    """
    if not data:
        return

    html_table: str = tabulate(data, headers="keys", tablefmt="html")

    if not full_page:
        click.echo(html_table)
    else:
        html: str = f"""<!DOCTYPE html>
<html>
<head>
    <title>DNS Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .critical {{ color: red; font-weight: bold; }}
        .high {{ color: red; }}
        .medium {{ color: orange; }}
        .low {{ color: green; }}
    </style>
</head>
<body>
    <h1>DNS Poisoning Check Results</h1>
    <p>Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}</p>
    {html_table}
</body>
</html>"""
        click.echo(html)


def save_results(
    data: Any, filename: str, fileformat: Literal["json", "csv", "html", "html_table"]
) -> None:
    """Save results to a file in the specified format.

    Creates parent directories if they don't exist. Handles various file formats
    with appropriate formatting and error handling.

    Args:
        data: The data to save. Format depends on fileformat:
            - JSON: Any JSON-serializable data
            - CSV: List of dictionaries with consistent keys
            - HTML/HTML_TABLE: List of dictionaries for tabulate formatting
        filename: Path where the file should be saved.
        fileformat: Output format:
            - "json": JSON format with indentation
            - "csv": CSV format with headers
            - "html": Complete HTML page with styling
            - "html_table": Raw HTML table only

    Returns:
        None: Results are saved to file, success/error messages printed to console.

    Raises:
        Prints error messages to console but does not raise exceptions.
    """
    try:
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if fileformat == "json":
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            click.secho(f"JSON results saved to {file_path}", fg="green")

        elif fileformat == "csv":
            with file_path.open("w", encoding="utf-8", newline="") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            click.secho(f"CSV results saved to {file_path}", fg="green")

        elif fileformat == "html":
            with file_path.open("w", encoding="utf-8") as f:
                html_table = tabulate(data, headers="keys", tablefmt="html")
                html = f"""<!DOCTYPE html>
<html>
<head>
    <title>DNS Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>DNS Analysis Results</h1>
    <p>Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}</p>
    {html_table}
</body>
</html>"""
                f.write(html)
            click.secho(f"HTML results saved to {file_path}", fg="green")

        elif fileformat == "html_table":
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="html"))
            click.secho(f"HTML table results saved to {file_path}", fg="green")

        else:
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="grid"))
            click.secho(f"Table results saved to {file_path}", fg="green")

    except PermissionError:
        click.secho(
            f"Permission denied: Cannot write to {filename}", fg="red", err=True
        )
    except OSError as e:
        click.secho(f"OS error while saving results: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"Failed to save results: {e}", fg="red", err=True)


def format_dns_record(
    results: Sequence[dict[str, Any]],
    style: Literal["standard", "short"] = "standard",
    *,
    show_ttl: bool = False,
) -> list[dict[str, Any]]:
    """Format DNS records in different display styles.

    Transforms raw DNS record data into human-readable formats suitable for
    different display contexts.

    Args:
        results: List of DNS query results. Each result should contain:
            - domain: The queried domain name
            - records: Dictionary mapping record types to their data
        style: Output style:
            - "standard": One row per domain with all record types
            - "short": One row per individual record (flattened)
        show_ttl: If True, include TTL values in record display (default: False).

    Returns:
        list[dict]: Formatted records ready for display. Structure depends on style.

    Example (standard style):
        >>> data = [
        ...     {"domain": "example.com", "records": {"A": {"records": ["1.2.3.4"]}}}
        ... ]
        >>> format_dns_record(data, style="standard")
        [{"domain": "example.com", "A": "1.2.3.4"}]

    Example (short style):
        >>> format_dns_record(data, style="short")
        [{"domain": "example.com", "type": "A", "value": "1.2.3.4"}]
    """
    formatted: list[dict[str, Any]] = []

    for result in results:
        if style == "short":
            transformed_list: list[dict[str, str | int]] = []
            transformed_list.extend(
                [
                    {
                        "domain": result["domain"],
                        "type": rtype,
                        "value": record,
                    }
                    for result in results
                    for rtype, records in result["records"].items()
                    for record in records.get("records", [])
                ]
            )
            return transformed_list
        row: dict[str, Any] = {"domain": result["domain"]}
        for rtype, data in result["records"].items():
            if data.get("records"):
                if show_ttl and data.get("ttl"):
                    values: list[str] = [
                        f"{r} (TTL: {data['ttl']}s)" for r in data["records"]
                    ]
                else:
                    values = data["records"]
                row[rtype] = "\n".join(values)
            elif data.get("error"):
                row[rtype] = f"[{data['error']}]"
            else:
                row[rtype] = "None"
        formatted.append(row)

    return formatted


def _format_scan_results(
    results: list[ScanResult], *, show_closed: bool
) -> list[dict[str, Any]]:
    """Format scan results for CLI output."""
    formatted: list[dict[str, str]] = []

    for result in results:
        if not result.open_ports and not show_closed:
            formatted.append(
                {
                    "target": result.target,
                    "ip": result.target_ip,
                    "port": "—",
                    "state": "NO OPEN PORTS",
                    "service": "—",
                    "banner": "—",
                    "response_time_ms": "—",
                }
            )
            continue

        for port, port_result in sorted(result.results.items()):
            if port_result.state == "open" or show_closed:
                formatted.append(
                    {
                        "target": result.target,
                        "ip": result.target_ip,
                        "port": str(port),
                        "state": port_result.state.upper(),
                        "service": port_result.service,
                        "banner": port_result.banner or "",
                        "response_time_ms": (
                            str(port_result.response_time)
                            if port_result.response_time
                            else ""
                        ),
                    }
                )

    return formatted


def format_dns_trace(trace_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Format DNS trace route results for tabular display.

    Converts a DNS trace result into a list of dictionaries suitable for
    table formatting, showing each hop in the resolution path.

    Args:
        trace_result: Dictionary containing trace results with:
            - hops: List of intermediate DNS server responses
            - final_answer: Optional final authoritative response

    Returns:
        list[dict]: Formatted trace data with columns:
            - hop: Hop number in the trace
            - nameserver: Server that responded
            - response_time: Response time in ms or "timeout"
            - records: DNS records returned (joined with newlines)
            - next: Next nameserver to query

    Example:
        >>> trace = {"hops": [{"nameserver": "8.8.8.8", "response_time": 42}]}
        >>> format_dns_trace(trace)
        [{"hop": 0, "nameserver": "8.8.8.8", "response_time": "42.00ms", ...}]
    """
    formatted: list[dict[str, int | str]] = []

    hops = trace_result.get("hops", [])

    for i, hop in enumerate(hops):
        response_time = hop.get("response_time")
        if response_time is None:
            time_str = "timeout"
        elif isinstance(response_time, int | float):
            time_str = f"{response_time:.2f}ms"
        else:
            time_str = str(response_time)

        records = hop.get("records", [])
        if records:
            records_str: str = "\n".join(str(r) for r in records)
        else:
            records_str = hop.get("error", "No records")

        formatted.append(
            {
                "hop": i,
                "nameserver": hop.get("nameserver", "N/A"),
                "response_time": time_str,
                "records": records_str,
                "next": hop.get("next", "N/A"),
            }
        )

    final: Any | None = trace_result.get("final_answer")
    if final and final not in hops:
        response_time = final.get("response_time")
        time_str: str = f"{response_time:.2f}ms" if response_time else "N/A"

        formatted.append(
            {
                "hop": len(hops),
                "nameserver": final.get("nameserver", "N/A"),
                "response_time": time_str,
                "records": "\n".join(
                    str(r) for r in final.get("records", ["Answer received"])
                ),
                "next": "Complete",
            }
        )

    return formatted


def format_dns_comparison(comparison_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Format DNS server comparison results for display.

    Transforms comparison results showing differences between multiple DNS servers
    into a tabular format.

    Args:
        comparison_result: Dictionary containing:
            - servers: Dictionary mapping server names to their response data

    Returns:
        list[dict]: Formatted comparison data with columns:
            - server: DNS server name/identifier
            - type: Record type (A, AAAA, MX, etc.)
            - response_time_ms: Response time in milliseconds
            - records: Records returned (joined with newlines)
            - differs: "✓" if record differs from reference, else " "

    Example:
        >>> comp = {"servers": {"8.8.8.8": {"A": {"records": ["1.2.3.4"]}}}}
        >>> format_dns_comparison(comp)
        [{"server": "8.8.8.8", "type": "A", "response_time_ms": "N/A", ...}]
    """
    formatted: list[dict[str, str | int]] = []

    for server, results in comparison_result.get("servers", {}).items():
        for rtype, data in results.items():
            row: dict[str, str | int] = {
                "server": server,
                "type": rtype,
                "response_time_ms": data.get("response_time", "N/A"),
                "records": "\n".join(data.get("records", ["None"])),
                "differs": "✓" if data.get("differs") else " ",
            }
            formatted.append(row)

    return formatted


def format_dns_health(health_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Format DNS health check results for tabular display.

    Converts health check results showing overall domain health and
    per-record-type scores into a readable format.

    Args:
        health_result: Dictionary containing:
            - domain: Domain name that was checked
            - score: Overall health score (0-100)
            - status: Overall status (healthy, warning, critical)
            - issues: List of detected issues
            - warnings: List of warnings
            - record_scores: Dictionary mapping record types to scores

    Returns:
        list[dict]: Formatted health data with:
            - domain: Domain name (indented for record types)
            - overall_score: Score as "X/100"
            - status: Uppercase status
            - issues: Issues (joined with newlines)
            - warnings: Warnings (joined with newlines)

    Example:
        >>> health = {"domain": "example.com", "score": 85, "status": "healthy"}
        >>> format_dns_health(health)
        [{"domain": "example.com", "overall_score": "85/100", ...}]
    """
    formatted: list[dict[str, str | int]] = [
        {
            "domain": health_result.get("domain"),
            "overall_score": f"{health_result.get('score', 0)}/100",
            "status": health_result.get("status", "unknown").upper(),
            "issues": "\n".join(health_result.get("issues", ["None"])),
            "warnings": "\n".join(health_result.get("warnings", ["None"])),
        }
    ]

    for record_type, score in health_result.get("record_scores", {}).items():
        formatted.append(
            {
                "domain": f"  {record_type}:",
                "overall_score": f"{score}/100",
                "status": "GOOD" if score >= 80 else "WARN" if score >= 50 else "BAD",
                "issues": "",
                "warnings": "",
            }
        )

    return formatted


def format_dns_poisoning(  # noqa: C901
    poisoning_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Format DNS poisoning check results with detailed analysis.

    Creates a comprehensive, human-readable breakdown of DNS poisoning test
    results, including server analysis, CDN detection, and verdict.

    Args:
        poisoning_result: Dictionary containing poisoning check results with:
            - domain: Domain that was tested
            - record_type: DNS record type tested
            - poisoning_level: Detected poisoning level
            - confidence: Confidence percentage in detection
            - cdn_detected: Whether CDN was detected
            - control_server: Control server used
            - test_servers_count: Number of servers tested
            - mismatches: Count of mismatching responses
            - inconsistencies: List of detected inconsistencies
            - and many other detailed metrics

    Returns:
        list[dict]: Formatted analysis data with columns:
            - section: Section header or detail prefix
            - detail: Primary information
            - value: Secondary value/metric
            - note: Additional context or explanation

    The output is organized into logical sections:
        - DNS ANALYSIS: Basic test info
        - CONTROL SERVER: Reference server details
        - SUMMARY: Overall statistics
        - CDN DETECTION: If CDN detected
        - VERDICT: Final determination

    Example:
        >>> result = {"domain": "example.com", "poisoning_level": "NONE"}
        >>> format_dns_poisoning(result)
        [{"section": "DNS ANALYSIS", "detail": "example.com (A)", ...}]
    """
    formatted: list[dict[str, str]] = []

    domain = poisoning_result.get("domain", "")
    record_type = poisoning_result.get("record_type", "A")
    level = poisoning_result.get("poisoning_level", "UNKNOWN")
    confidence = poisoning_result.get("confidence", 0)
    cdn_detected = poisoning_result.get("cdn_detected", False)
    cdn_owner = poisoning_result.get("cdn_owner", "Unknown")
    cdn_percentage = poisoning_result.get("cdn_percentage", 0)

    # Header
    status_text: Literal["CDN DETECTED", "POISONING CHECK"] = (
        "CDN DETECTED" if cdn_detected else "POISONING CHECK"
    )
    formatted.append(
        {
            "section": "DNS ANALYSIS",
            "detail": f"{domain} ({record_type})",
            "value": f"{level} (confidence: {confidence}%)",
            "note": f"{status_text}",
        }
    )

    # Control server info
    control = poisoning_result.get("control_server", "")
    control_name = poisoning_result.get("control_name", "Unknown")
    control_country = poisoning_result.get("control_country", "Unknown")
    control_records = poisoning_result.get("control_result", {}).get("records", [])
    control_owner = poisoning_result.get("control_owner", "Unknown")

    formatted.append(
        {
            "section": "CONTROL SERVER",
            "detail": f"{control} ({control_name}, {control_country})",
            "value": f"{len(control_records)} IPs",
            "note": f"Owner: {control_owner}",
        }
    )

    # IP analysis
    control_analysis = poisoning_result.get("control_analysis", {})
    if control_analysis:
        owners: set[str] = set(control_analysis.get("owners", []))
        owner_str: Literal["Unknown"] | str = ", ".join(owners) if owners else "Unknown"
        formatted.append(
            {
                "section": "CONTROL IP ANALYSIS",
                "detail": f"Unique: {control_analysis.get('unique', 0)} | IPv4: {control_analysis.get('ipv4', 0)} | IPv6: {control_analysis.get('ipv6', 0)}",  # noqa: E501
                "value": f"Owner: {owner_str}",
                "note": f"Private: {control_analysis.get('private', 0)} | Reserved: {control_analysis.get('reserved', 0)}",  # noqa: E501
            }
        )

    # Summary stats
    total = poisoning_result.get("test_servers_count", 0)
    mismatches = poisoning_result.get("mismatches", 0)
    cdn_variations = poisoning_result.get("cdn_variations", 0)
    severity = poisoning_result.get("severity", {})
    unique_ips = poisoning_result.get("unique_ips_seen", 0)

    formatted.append(
        {
            "section": "SUMMARY",
            "detail": f"Servers tested: {total}",
            "value": f"Mismatches: {mismatches} | CDN variations: {cdn_variations}",
            "note": f"High: {severity.get('high', 0)} Med: {severity.get('medium', 0)} Low: {severity.get('low', 0)} Info: {severity.get('info', 0)}",  # noqa: E501
        }
    )

    # CDN detection
    if cdn_detected:
        formatted.append(
            {
                "section": "CDN DETECTION",
                "detail": f"CDN Provider: {cdn_owner}",
                "value": f"{cdn_percentage}% of IPs match",
                "note": "Different IPs from same provider - normal CDN behavior",
            }
        )

    # IP diversity
    ip_diversity = poisoning_result.get("ip_diversity", 0)
    formatted.append(
        {
            "section": "IP DIVERSITY",
            "detail": f"Unique IPs seen: {unique_ips}",
            "value": f"IPs outside control: {ip_diversity}",
            "note": f"Geo diversity: {poisoning_result.get('geo_diversity', 0)} countries",  # noqa: E501
        }
    )

    # Consensus
    consensus = poisoning_result.get("consensus_top", [])
    if consensus:
        top = consensus[0]
        formatted.append(
            {
                "section": "CONSENSUS",
                "detail": f"Most common IP: {top['ip']}",
                "value": f"{top['percentage']}% of servers",
                "note": f"Owner: {top.get('owner', 'Unknown')} | Consensus rate: {poisoning_result.get('consensus_rate', 0)}%",  # noqa: E501
            }
        )

    # Analysis verdict
    if poisoning_result.get("cdn_likely"):
        formatted.append(
            {
                "section": "ANALYSIS",
                "detail": "CDN NETWORK DETECTED",
                "value": "Normal behavior",
                "note": "Different IPs per region expected - not poisoning",
            }
        )
    elif poisoning_result.get("anycast_likely"):
        formatted.append(
            {
                "section": "ANALYSIS",
                "detail": "Anycast/GeoDNS detected",
                "value": "Normal CDN behavior",
                "note": "Different IPs per region expected",
            }
        )
    elif poisoning_result.get("poisoning_likely"):
        formatted.append(
            {
                "section": "ANALYSIS",
                "detail": "SUSPICIOUS PATTERN",
                "value": "Possible DNS poisoning",
                "note": "All servers return same wrong IP",
            }
        )

    # Detailed inconsistencies
    if poisoning_result.get("inconsistencies"):
        formatted.append(
            {
                "section": "DETAILS",
                "detail": "",
                "value": "",
                "note": "",
            }
        )

        for inc in poisoning_result["inconsistencies"][:5]:
            server = inc["server"]
            sname = inc.get("server_name", "Unknown")
            country = inc.get("server_country", "??")
            itype = inc["type"].replace("_", " ").title()
            severity = inc["severity"].upper()

            if itype == "Cdn Variation":
                note: str = (
                    f"CDN node variation - same provider: {inc.get('owner', 'Unknown')}"
                )
            elif itype == "Record Mismatch":
                control_owner = inc.get("control_owner", "Unknown")
                test_owner = inc.get("test_owner", "Unknown")
                note: str = f"Control owner: {control_owner} | Test owner: {test_owner}"
            elif itype == "Error Mismatch":
                note: str = f"Control error: {inc['control_error']} | Test error: {inc['test_error']}"  # noqa: E501
            else:
                note: str = f"TTL diff: {inc['diff']}s"

            formatted.append(
                {
                    "section": f"  -> {server} ({sname}, {country})",
                    "detail": f"[{severity}] {itype}",
                    "value": "",
                    "note": note[:60] + "..." if len(note) > 60 else note,
                }
            )

    # Final verdict
    if poisoning_result.get("cdn_detected"):
        verdict = "CLEAN (CDN DETECTED)"
        explanation: str = f"Different {cdn_owner} CDN nodes - normal behavior"
    elif not poisoning_result.get("poisoned"):
        verdict = "CLEAN"
        explanation: str = "No inconsistencies detected"
    else:
        verdict = "POISONED"
        explanation: str = f"{mismatches}/{total} servers show inconsistencies"

    formatted.append(
        {
            "section": "VERDICT",
            "detail": verdict,
            "value": f"Level: {poisoning_result.get('poisoning_level', 'NONE')}",
            "note": explanation,
        }
    )

    return formatted
