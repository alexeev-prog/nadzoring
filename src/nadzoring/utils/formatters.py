# nadzoring/utils/formatters.py
"""Output formatting utilities for CLI commands."""

import csv
import json
import shutil
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Literal

import click
from tabulate import tabulate

OutputFormat = Literal["table", "json", "csv", "html", "html_table"]


def get_terminal_width() -> int:
    """Return current terminal width in columns."""
    return shutil.get_terminal_size().columns


def truncate_string(s: str, max_width: int, placeholder: str = "...") -> str:
    """Truncate string to fit within specified width."""
    if len(s) <= max_width:
        return s
    return s[: max_width - len(placeholder)] + placeholder


def colorize_value(value: Any, *, no_color: bool = False) -> str:
    """Apply color formatting to values based on content."""
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
    data: list[dict], tablefmt: str = "simple_grid", *, no_color: bool = False
) -> None:
    """Print results as formatted table that fits terminal width."""
    if not data:
        click.echo("No results to display")
        return

    if not no_color:
        data = [
            {key: colorize_value(value) for key, value in row.items()} for row in data
        ]

    term_width = get_terminal_width()
    headers = list(data[0].keys())

    min_widths = {h: len(h) for h in headers}
    max_widths = dict.fromkeys(headers, 80)

    special_limits = {"TXT": 60, "AAAA": 40, "A": 30, "MX": 40, "NS": 40, "SOA": 60}
    for h, w in special_limits.items():
        if h in max_widths:
            max_widths[h] = w

    borders = len(headers) * 3 + 1
    available = term_width - borders

    if available <= 0:
        widths = [min_widths[h] for h in headers]
    else:
        widths = _calculate_column_widths(headers, min_widths, max_widths, available)

    try:
        output = tabulate(
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


def _calculate_column_widths(headers, min_widths, max_widths, available):
    """Calculate optimal column widths within available space."""
    total_min = sum(min_widths.values())

    if total_min >= available:
        return [min_widths[h] for h in headers]

    extra = (available - total_min) / len(headers)
    col_widths = {}

    for h in headers:
        new = int(min_widths[h] + extra)
        col_widths[h] = min(new, max_widths[h])

    total = sum(col_widths.values())
    if total <= available:
        return [col_widths[h] for h in headers]

    overflow = total - available
    sorted_cols = sorted(headers, key=lambda h: col_widths[h], reverse=True)

    for h in sorted_cols:
        if overflow <= 0:
            break
        reduction = min(overflow, col_widths[h] - min_widths[h])
        col_widths[h] -= reduction
        overflow -= reduction

    return [col_widths[h] for h in headers]


def print_csv_table(data: list[dict]) -> None:
    """Print data as CSV to console."""
    if not data:
        click.echo("No data to display")
        return

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    click.echo(output.getvalue())


def print_html_table(data: list[dict], *, full_page: bool = False) -> None:
    """Print results as HTML table or complete HTML page."""
    if not data:
        return

    html_table = tabulate(data, headers="keys", tablefmt="html")

    if not full_page:
        click.echo(html_table)
    else:
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


def save_results(data: Any, filename: str, fileformat: str) -> None:
    """Save results to file in specified format."""
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
    results: list[dict], style: str = "standard", *, show_ttl: bool = False
) -> list[dict]:
    """Format DNS records in different styles for display."""
    formatted = []

    for result in results:
        if style == "short":
            transformed_list = []
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
        row = {"domain": result["domain"]}
        for rtype, data in result["records"].items():
            if data.get("records"):
                if show_ttl and data.get("ttl"):
                    values = [f"{r} (TTL: {data['ttl']}s)" for r in data["records"]]
                else:
                    values = data["records"]
                row[rtype] = "\n".join(values)
            elif data.get("error"):
                row[rtype] = f"[{data['error']}]"
            else:
                row[rtype] = "None"
        formatted.append(row)

    return formatted


def format_dns_trace(trace_result: dict) -> list[dict[str, Any]]:
    """Format DNS trace results for display."""
    formatted = []

    hops = trace_result.get("hops", [])

    for i, hop in enumerate(hops):
        response_time = hop.get("response_time")
        if response_time is None:
            time_str = "timeout"
        elif isinstance(response_time, (int, float)):
            time_str = f"{response_time:.2f}ms"
        else:
            time_str = str(response_time)

        records = hop.get("records", [])
        if records:
            records_str = "\n".join(str(r) for r in records)
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

    final = trace_result.get("final_answer")
    if final and final not in hops:
        response_time = final.get("response_time")
        time_str = f"{response_time:.2f}ms" if response_time else "N/A"

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


def format_dns_comparison(comparison_result: dict) -> list[dict]:
    """Format DNS comparison results for display."""
    formatted = []

    for server, results in comparison_result.get("servers", {}).items():
        for rtype, data in results.items():
            row = {
                "server": server,
                "type": rtype,
                "response_time_ms": data.get("response_time", "N/A"),
                "records": "\n".join(data.get("records", ["None"])),
                "differs": "✓" if data.get("differs") else " ",
            }
            formatted.append(row)

    return formatted


def format_dns_health(health_result: dict) -> list[dict]:
    """Format DNS health check results for display."""
    formatted = [
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


def format_dns_poisoning(poisoning_result: dict) -> list[dict]:  # noqa: C901
    """Format DNS poisoning check results with detailed analysis."""
    formatted = []

    domain = poisoning_result.get("domain", "")
    record_type = poisoning_result.get("record_type", "A")
    level = poisoning_result.get("poisoning_level", "UNKNOWN")
    confidence = poisoning_result.get("confidence", 0)
    cdn_detected = poisoning_result.get("cdn_detected", False)
    cdn_owner = poisoning_result.get("cdn_owner", "Unknown")
    cdn_percentage = poisoning_result.get("cdn_percentage", 0)

    # Header
    status_text = "CDN DETECTED" if cdn_detected else "POISONING CHECK"
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
        owners = set(control_analysis.get("owners", []))
        owner_str = ", ".join(owners) if owners else "Unknown"
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
                note = (
                    f"CDN node variation - same provider: {inc.get('owner', 'Unknown')}"
                )
            elif itype == "Record Mismatch":
                control_owner = inc.get("control_owner", "Unknown")
                test_owner = inc.get("test_owner", "Unknown")
                note = f"Control owner: {control_owner} | Test owner: {test_owner}"
            elif itype == "Error Mismatch":
                note = f"Control error: {inc['control_error']} | Test error: {inc['test_error']}"  # noqa: E501
            else:
                note = f"TTL diff: {inc['diff']}s"

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
        explanation = f"Different {cdn_owner} CDN nodes - normal behavior"
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
