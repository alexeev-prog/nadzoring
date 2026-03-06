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

_HTML_STYLES = """\
    body { font-family: Arial, sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #4CAF50; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    .critical { color: red; font-weight: bold; }
    .high { color: red; }
    .medium { color: orange; }
    .low { color: green; }"""

_CRITICAL_TERMS: set[str] = {"CRITICAL", "HIGH", "POISONED", "ERROR", "NXDOMAIN"}
_WARNING_TERMS: set[str] = {"MEDIUM", "WARNING", "MISMATCH", "TTL_DIFF"}
_INFO_TERMS: set[str] = {"LOW", "INFO", "REFERENCE", "CLEAN"}
_POSITIVE_TERMS: set[str] = {"yes", "up", "passed", "good", "healthy"}


def get_terminal_width() -> int:
    """
    Return the current terminal width in columns.

    Falls back to a sensible default when the terminal size cannot be
    determined.

    Returns:
        Number of columns available in the terminal.

    """
    return shutil.get_terminal_size().columns


def truncate_string(s: str, max_width: int, placeholder: str = "...") -> str:
    """
    Truncate *s* to fit within *max_width* characters.

    If *s* is already within the limit it is returned unchanged. Otherwise
    it is shortened and *placeholder* is appended to signal truncation.

    Args:
        s: The string to truncate.
        max_width: Maximum allowed length in characters.
        placeholder: Suffix appended to truncated strings. Defaults to
            ``"..."``.

    Returns:
        Original string when within limits; truncated string with
        placeholder otherwise.

    Examples:
        >>> truncate_string("very long string", 10)
        'very lo...'

    """
    if len(s) <= max_width:
        return s
    return s[: max_width - len(placeholder)] + placeholder


def colorize_value(value: Any, *, no_color: bool = False) -> str:
    r"""
    Apply ANSI colour formatting to a value based on its semantic meaning.

    Colours are chosen by matching the uppercased string against severity
    keyword sets:

    * Red/bold — critical/error terms (``CRITICAL``, ``HIGH``, …)
    * Yellow/bold — warning terms (``MEDIUM``, ``WARNING``, …)
    * Green — informational/positive terms (``LOW``, ``yes``, ``up``, …)

    Args:
        value: Value to format. Converted to ``str`` before matching.
        no_color: When ``True`` colours are disabled and the plain string
            is returned. Defaults to ``False``.

    Returns:
        ANSI-coloured string, or a plain string when *no_color* is ``True``
        or the value does not match any keyword set.

    Examples:
        >>> colorize_value("CRITICAL")
        '\x1b[1;31mCRITICAL\x1b[0m'

    """
    value_str = str(value)

    if no_color or not isinstance(value, str):
        return value_str

    upper: str = value.upper()
    lower: str = value.lower()

    if upper in _CRITICAL_TERMS:
        return click.style(value_str, fg="red", bold=True)
    if upper in _WARNING_TERMS:
        return click.style(value_str, fg="yellow", bold=True)
    if upper in _INFO_TERMS or lower in _POSITIVE_TERMS:
        return click.style(value_str, fg="green")

    return value_str


def print_results_table(
    data: Sequence[dict[str, Any]],
    tablefmt: str = "simple_grid",
    *,
    no_color: bool = False,
) -> None:
    """
    Print a formatted table that fits the current terminal width.

    Column widths are calculated automatically; special DNS record type
    columns (``TXT``, ``AAAA``, etc.) have predefined maximum widths.

    Args:
        data: Rows to display. Each dict must have the same keys.
        tablefmt: ``tabulate`` format string. Defaults to
            ``"simple_grid"``.
        no_color: Disable colour formatting when ``True``. Defaults to
            ``False``.

    """
    if not data:
        click.echo("No results to display")
        return

    if not no_color:
        data = [
            {key: colorize_value(value) for key, value in row.items()} for row in data
        ]

    term_width = get_terminal_width()
    headers = list(data[0].keys())

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

    widths: list[int] = (
        [min_widths[h] for h in headers]
        if available <= 0
        else _calculate_column_widths(headers, min_widths, max_widths, available)
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
        output = tabulate(data, headers="keys", tablefmt="simple")

    click.echo(output)


def _calculate_column_widths(
    headers: list[str],
    min_widths: dict[str, int],
    max_widths: dict[str, int],
    available: int,
) -> list[int]:
    """
    Distribute *available* width across columns, respecting per-column limits.

    Extra space beyond the minimum widths is divided equally; the result is
    clamped to each column's maximum. If the total still exceeds *available*,
    the widest columns are trimmed first.

    Args:
        headers: Column header names (defines ordering).
        min_widths: Minimum character width per column.
        max_widths: Maximum character width per column.
        available: Total character budget for all columns combined.

    Returns:
        List of integer column widths in the same order as *headers*.

    """
    total_min: Literal[0] | int = sum(min_widths.values())

    if total_min >= available:
        return [min_widths[h] for h in headers]

    extra: float = (available - total_min) / len(headers)
    col_widths: dict[str, int] = {
        h: min(int(min_widths[h] + extra), max_widths[h]) for h in headers
    }

    overflow = sum(col_widths.values()) - available
    if overflow > 0:
        for h in sorted(headers, key=lambda h: col_widths[h], reverse=True):
            if overflow <= 0:
                break
            reduction = min(overflow, col_widths[h] - min_widths[h])
            col_widths[h] -= reduction
            overflow -= reduction

    return [col_widths[h] for h in headers]


def print_csv_table(data: Sequence[dict[str, Any]]) -> None:
    """
    Print *data* in CSV format to standard output.

    Args:
        data: Rows to format. All dicts should share the same keys for
            well-formed CSV output.

    Examples:
        >>> print_csv_table([{"domain": "example.com", "ip": "1.2.3.4"}])
        domain,ip
        example.com,1.2.3.4

    """
    if not data:
        click.echo("No data to display")
        return

    output = StringIO()
    writer: DictWriter[str] = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    click.echo(output.getvalue())


def _build_html_page(title: str, html_table: str) -> str:
    """
    Wrap an HTML table fragment in a complete, styled HTML page.

    Args:
        title: Page ``<title>`` and ``<h1>`` heading text.
        html_table: Raw HTML ``<table>`` string to embed.

    Returns:
        Complete HTML document as a string.

    """
    timestamp: str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
{_HTML_STYLES}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {timestamp}</p>
    {html_table}
</body>
</html>"""


def print_html_table(
    data: Sequence[dict[str, Any]], *, full_page: bool = False
) -> None:
    """
    Print results as an HTML table or complete HTML page.

    Args:
        data: Rows to render as an HTML table.
        full_page: When ``True`` a complete HTML document with inline CSS
            styling is generated. When ``False`` only the ``<table>``
            element is printed. Defaults to ``False``.

    """
    if not data:
        return

    html_table: str = tabulate(data, headers="keys", tablefmt="html")

    if not full_page:
        click.echo(html_table)
    else:
        click.echo(_build_html_page("Nadzoring Results", html_table))


def save_results(
    data: Any,
    filename: str,
    fileformat: str,
) -> None:
    """
    Save command results to a file in the specified format.

    Creates parent directories automatically when they do not exist.
    Errors are reported to stderr via :func:`click.secho` rather than
    raising exceptions so that the CLI remains user-friendly.

    Args:
        data: Data to persist. Structure depends on *fileformat*:
            JSON — any JSON-serialisable object; CSV / HTML — list of
            dicts with consistent keys.
        filename: Destination file path.
        fileformat: One of ``"json"``, ``"csv"``, ``"html"``,
            ``"html_table"``, or any other value (falls back to plain
            ``tabulate`` grid output).

    """
    try:
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if fileformat == "json":
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        elif fileformat == "csv":
            with file_path.open("w", encoding="utf-8", newline="") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)

        elif fileformat == "html":
            html_table = tabulate(data, headers="keys", tablefmt="html")
            with file_path.open("w", encoding="utf-8") as f:
                f.write(_build_html_page("Nadzoring Analysis Results", html_table))

        elif fileformat == "html_table":
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="html"))

        else:
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="grid"))

        click.secho(f"Results saved to {file_path}", fg="green")

    except PermissionError:
        click.secho(
            f"Permission denied: cannot write to {filename}", fg="red", err=True
        )
    except OSError as exc:
        click.secho(f"OS error while saving results: {exc}", fg="red", err=True)
    except Exception as exc:
        click.secho(f"Failed to save results: {exc}", fg="red", err=True)


def format_dns_record(
    results: Sequence[dict[str, Any]],
    style: str = "standard",
    *,
    show_ttl: bool = False,
) -> list[dict[str, Any]]:
    """
    Format DNS records into a display-ready list of dicts.

    Args:
        results: Raw DNS query results. Each item must contain
            ``domain`` and ``records`` keys.
        style: Output style — ``"short"`` produces one row per record
            value; any other value produces one row per domain.
        show_ttl: When ``True``, TTL values are appended to each record
            string in standard style. Defaults to ``False``.

    Returns:
        Formatted records ready for display.

    Examples:
        >>> data = [
        ...     {"domain": "example.com", "records": {"A": {"records": ["1.2.3.4"]}}}
        ... ]
        >>> format_dns_record(data, style="standard")
        [{'domain': 'example.com', 'A': '1.2.3.4'}]
        >>> format_dns_record(data, style="short")
        [{'domain': 'example.com', 'type': 'A', 'value': '1.2.3.4'}]

    """
    if style == "short":
        return [
            {"domain": result["domain"], "type": rtype, "value": record}
            for result in results
            for rtype, rdata in result["records"].items()
            for record in rdata.get("records", [])
        ]

    formatted: list[dict[str, Any]] = []

    for result in results:
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


def format_scan_results(
    results: list[ScanResult], *, show_closed: bool
) -> list[dict[str, Any]]:
    """
    Convert :class:`ScanResult` objects into CLI-displayable dicts.

    Public alias for the internal formatter used by network commands.

    Args:
        results: Port scan results to format.
        show_closed: When ``True``, closed/filtered ports are included
            alongside open ones.

    Returns:
        List of flat dicts with ``target``, ``ip``, ``port``, ``state``,
        ``service``, ``banner``, and ``response_time_ms`` keys.

    """
    return _format_scan_results(results, show_closed=show_closed)


def _format_scan_results(
    results: list[ScanResult], *, show_closed: bool
) -> list[dict[str, Any]]:
    """
    Convert :class:`ScanResult` objects into CLI-displayable dicts.

    Args:
        results: Port scan results to format.
        show_closed: When ``True``, closed/filtered ports are included
            alongside open ones.

    Returns:
        List of flat dicts with ``target``, ``ip``, ``port``, ``state``,
        ``service``, ``banner``, and ``response_time_ms`` keys.

    """
    formatted: list[dict[str, Any]] = []

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
    """
    Format a DNS trace result for tabular display.

    Args:
        trace_result: Raw trace dict with ``hops`` (list) and optional
            ``final_answer`` keys.

    Returns:
        List of dicts with ``hop``, ``nameserver``, ``response_time``,
        ``records``, and ``next`` columns.

    Examples:
        >>> trace = {"hops": [{"nameserver": "8.8.8.8", "response_time": 42}]}
        >>> format_dns_trace(trace)[0]["nameserver"]
        '8.8.8.8'

    """
    formatted: list[dict[str, Any]] = []
    hops: list[dict[str, Any]] = trace_result.get("hops", [])

    for i, hop in enumerate(hops):
        response_time: Any | None = hop.get("response_time")

        if response_time is None:
            time_str = "timeout"
        elif isinstance(response_time, int | float):
            time_str: str = f"{response_time:.2f}ms"
        else:
            time_str = str(response_time)

        records = hop.get("records", [])
        records_str: str | Any = (
            "\n".join(str(r) for r in records)
            if records
            else hop.get("error", "No records")
        )

        formatted.append(
            {
                "hop": i,
                "nameserver": hop.get("nameserver", "N/A"),
                "response_time": time_str,
                "records": records_str,
                "next": hop.get("next", "N/A"),
            }
        )

    final: dict[str, Any] | None = trace_result.get("final_answer")
    if final and final not in hops:
        response_time = final.get("response_time")
        time_str = f"{response_time:.2f}ms" if response_time else "N/A"
        final_records = final.get("records", ["Answer received"])

        formatted.append(
            {
                "hop": len(hops),
                "nameserver": final.get("nameserver", "N/A"),
                "response_time": time_str,
                "records": "\n".join(str(r) for r in final_records),
                "next": "Complete",
            }
        )

    return formatted


def format_dns_comparison(comparison_result: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Format DNS comparison results for tabular display.

    Args:
        comparison_result: Dict with a ``servers`` key mapping server
            names to per-type response data.

    Returns:
        List of dicts with ``server``, ``type``, ``response_time_ms``,
        ``records``, and ``differs`` columns.

    Examples:
        >>> comp = {"servers": {"8.8.8.8": {"A": {"records": ["1.2.3.4"]}}}}
        >>> format_dns_comparison(comp)[0]["server"]
        '8.8.8.8'

    """
    return [
        {
            "server": server,
            "type": rtype,
            "response_time_ms": data.get("response_time", "N/A"),
            "records": "\n".join(data.get("records", ["None"])),
            "differs": "✓" if data.get("differs") else " ",
        }
        for server, results in comparison_result.get("servers", {}).items()
        for rtype, data in results.items()
    ]


def format_dns_health(health_result: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Format DNS health check results for tabular display.

    Args:
        health_result: Dict with ``domain``, ``score``, ``status``,
            ``issues``, ``warnings``, and ``record_scores`` keys.

    Returns:
        List of dicts: one summary row followed by per-record-type rows.

    Examples:
        >>> health = {
        ...     "domain": "example.com",
        ...     "score": 85,
        ...     "status": "healthy",
        ...     "issues": [],
        ...     "warnings": [],
        ...     "record_scores": {},
        ... }
        >>> format_dns_health(health)[0]["overall_score"]
        '85/100'

    """
    score = health_result.get("score", 0)
    summary: dict[str, Any] = {
        "domain": health_result.get("domain"),
        "overall_score": f"{score}/100",
        "status": health_result.get("status", "unknown").upper(),
        "issues": "\n".join(health_result.get("issues", ["None"])),
        "warnings": "\n".join(health_result.get("warnings", ["None"])),
    }

    rows: list[dict[str, Any]] = [summary]

    for record_type, record_score in health_result.get("record_scores", {}).items():
        status: Literal['BAD', 'GOOD', 'WARN'] = (
            "GOOD" if record_score >= 80 else "WARN" if record_score >= 50 else "BAD"
        )
        rows.append(
            {
                "domain": f"  {record_type}:",
                "overall_score": f"{record_score}/100",
                "status": status,
                "issues": "",
                "warnings": "",
            }
        )

    return rows


def format_dns_poisoning(  # noqa: C901
    poisoning_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Build a detailed, human-readable breakdown of a DNS poisoning check.

    The result is organised into logical sections (DNS ANALYSIS, CONTROL
    SERVER, SUMMARY, CDN DETECTION, IP DIVERSITY, CONSENSUS, ANALYSIS,
    DETAILS, VERDICT) and returned as a flat list of rows suitable for
    table rendering.

    Args:
        poisoning_result: Poisoning check result dict as returned by
            :func:`nadzoring.dns_lookup.check_dns_poisoning`.

    Returns:
        List of dicts with ``section``, ``detail``, ``value``, and
        ``note`` columns.

    Examples:
        >>> result = {
        ...     "domain": "example.com",
        ...     "poisoning_level": "NONE",
        ...     "confidence": 100,
        ...     "cdn_detected": False,
        ...     "poisoned": False,
        ... }
        >>> format_dns_poisoning(result)[-1]["detail"]
        'CLEAN'

    """
    formatted: list[dict[str, str]] = []

    domain = poisoning_result.get("domain", "")
    record_type = poisoning_result.get("record_type", "A")
    level = poisoning_result.get("poisoning_level", "UNKNOWN")
    confidence = poisoning_result.get("confidence", 0)
    cdn_detected = poisoning_result.get("cdn_detected", False)
    cdn_owner = poisoning_result.get("cdn_owner", "Unknown")
    cdn_percentage = poisoning_result.get("cdn_percentage", 0)

    status_text: Literal['CDN DETECTED', 'POISONING CHECK'] = "CDN DETECTED" if cdn_detected else "POISONING CHECK"
    formatted.append(
        {
            "section": "DNS ANALYSIS",
            "detail": f"{domain} ({record_type})",
            "value": f"{level} (confidence: {confidence}%)",
            "note": status_text,
        }
    )

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

    control_analysis = poisoning_result.get("control_analysis", {})
    if control_analysis:
        owners: set[str] = set(control_analysis.get("owners", []))
        owner_str = ", ".join(owners) if owners else "Unknown"
        formatted.append(
            {
                "section": "CONTROL IP ANALYSIS",
                "detail": (
                    f"Unique: {control_analysis.get('unique', 0)} | "
                    f"IPv4: {control_analysis.get('ipv4', 0)} | "
                    f"IPv6: {control_analysis.get('ipv6', 0)}"
                ),
                "value": f"Owner: {owner_str}",
                "note": (
                    f"Private: {control_analysis.get('private', 0)} | "
                    f"Reserved: {control_analysis.get('reserved', 0)}"
                ),
            }
        )

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
            "note": (
                f"High: {severity.get('high', 0)} "
                f"Med: {severity.get('medium', 0)} "
                f"Low: {severity.get('low', 0)} "
                f"Info: {severity.get('info', 0)}"
            ),
        }
    )

    if cdn_detected:
        formatted.append(
            {
                "section": "CDN DETECTION",
                "detail": f"CDN Provider: {cdn_owner}",
                "value": f"{cdn_percentage}% of IPs match",
                "note": "Different IPs from same provider - normal CDN behavior",
            }
        )

    ip_diversity = poisoning_result.get("ip_diversity", 0)
    formatted.append(
        {
            "section": "IP DIVERSITY",
            "detail": f"Unique IPs seen: {unique_ips}",
            "value": f"IPs outside control: {ip_diversity}",
            "note": f"Geo diversity: {poisoning_result.get('geo_diversity', 0)} countries",  # noqa: E501
        }
    )

    consensus = poisoning_result.get("consensus_top", [])
    if consensus:
        top = consensus[0]
        formatted.append(
            {
                "section": "CONSENSUS",
                "detail": f"Most common IP: {top['ip']}",
                "value": f"{top['percentage']}% of servers",
                "note": (
                    f"Owner: {top.get('owner', 'Unknown')} | "
                    f"Consensus rate: {poisoning_result.get('consensus_rate', 0)}%"
                ),
            }
        )

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

    inconsistencies = poisoning_result.get("inconsistencies", [])
    if inconsistencies:
        formatted.append({"section": "DETAILS", "detail": "", "value": "", "note": ""})

        for inc in inconsistencies[:5]:
            server = inc["server"]
            sname = inc.get("server_name", "Unknown")
            country = inc.get("server_country", "??")
            itype = inc["type"].replace("_", " ").title()
            inc_severity = inc["severity"].upper()

            if itype == "Cdn Variation":
                note: str = (
                    f"CDN node variation - same provider: {inc.get('owner', 'Unknown')}"
                )
            elif itype == "Record Mismatch":
                note = f"Control owner: {inc.get('control_owner', 'Unknown')} | Test owner: {inc.get('test_owner', 'Unknown')}"  # noqa: E501
            elif itype == "Error Mismatch":
                note = f"Control error: {inc['control_error']} | Test error: {inc['test_error']}"  # noqa: E501
            else:
                note = f"TTL diff: {inc['diff']}s"

            formatted.append(
                {
                    "section": f"  -> {server} ({sname}, {country})",
                    "detail": f"[{inc_severity}] {itype}",
                    "value": "",
                    "note": note[:60] + "..." if len(note) > 60 else note,
                }
            )

    if poisoning_result.get("cdn_detected"):
        verdict = "CLEAN (CDN DETECTED)"
        explanation: str = f"Different {cdn_owner} CDN nodes - normal behavior"
    elif not poisoning_result.get("poisoned"):
        verdict = "CLEAN"
        explanation = "No inconsistencies detected"
    else:
        verdict = "POISONED"
        explanation = f"{mismatches}/{total} servers show inconsistencies"

    formatted.append(
        {
            "section": "VERDICT",
            "detail": verdict,
            "value": f"Level: {poisoning_result.get('poisoning_level', 'NONE')}",
            "note": explanation,
        }
    )

    return formatted
