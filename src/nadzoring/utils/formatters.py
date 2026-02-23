# src/nadzoring/cli/utils/formatters.py
"""Output formatting utilities."""

import csv
import json
import shutil
from csv import DictWriter
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Literal

import click
from tabulate import tabulate

OutputFormat: type["OutputFormat"] = Literal[
    "table", "json", "csv", "html", "html_table"
]


def get_terminal_width() -> int:
    """Get terminal width for table formatting."""
    return shutil.get_terminal_size().columns


def truncate_string(s: str, max_width: int, placeholder: str = "...") -> str:
    """Truncate string to fit in terminal."""
    if len(s) <= max_width:
        return s
    return s[: max_width - len(placeholder)] + placeholder


def colorize_value(value: Any, *, no_color: bool = False) -> str:
    """Add color to values based on content."""
    if no_color:
        return str(value)

    value_str = str(value)

    if isinstance(value, str):
        if value.lower() in ["error", "failed", "no", "down", "none"]:
            return click.style(value_str, fg="red")
        if value.lower() in ["warning", "warn"]:
            return click.style(value_str, fg="yellow")
        if value.lower() in ["yes", "up", "passed", "good", "healthy"] or "✓" in value:
            return click.style(value_str, fg="green")

    return value_str


def print_results_table(
    data: list[dict], tablefmt: str = "simple_grid", *, no_color: bool = False
) -> None:
    """Print results as a formatted table with terminal width limiting."""
    if not data:
        click.echo("No results to display")
        return

    if not no_color:
        data = [
            {key: colorize_value(value) for key, value in row.items()} for row in data
        ]

    term_width: int = get_terminal_width()
    num_columns: int = len(data[0].keys())

    safe_col_width: int = max(10, (term_width - 10) // num_columns)

    try:
        output: str = tabulate(
            data,
            headers="keys",
            tablefmt=tablefmt,
            maxcolwidths=[safe_col_width] * num_columns,
            stralign="left",
            numalign="left",
        )

        if any(len(line) > term_width for line in output.split("\n")):
            output = tabulate(
                data,
                headers="keys",
                tablefmt="simple",
                maxcolwidths=[safe_col_width // 2] * num_columns,
                stralign="left",
                numalign="left",
            )
    except Exception:
        output = tabulate(data, headers="keys", tablefmt="simple")

    click.echo(output)


def print_csv_table(data: list[dict]) -> None:
    """Print data as CSV to console."""
    if not data:
        click.echo("No data to display")
        return

    output = StringIO()
    writer: DictWriter = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    click.echo(output.getvalue())


def print_html_table(data: list[dict], *, full_page: bool = False) -> None:
    """Print results as HTML."""
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
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .success {{ color: green; }}
    </style>
</head>
<body>
    <h1>DNS Analysis Results</h1>
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
            click.secho(f"✓ JSON results saved to {file_path}", fg="green")

        elif fileformat == "csv":
            with file_path.open("w", encoding="utf-8", newline="") as f:
                if data:
                    writer: DictWriter = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            click.secho(f"✓ CSV results saved to {file_path}", fg="green")

        elif fileformat == "html":
            with file_path.open("w", encoding="utf-8") as f:
                html_table: str = tabulate(data, headers="keys", tablefmt="html")
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
    </style>
</head>
<body>
    <h1>DNS Analysis Results</h1>
    <p>Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}</p>
    {html_table}
</body>
</html>"""
                f.write(html)
            click.secho(f"✓ HTML results saved to {file_path}", fg="green")

        elif fileformat == "html_table":
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="html"))
            click.secho(f"✓ HTML table results saved to {file_path}", fg="green")

        else:  # table
            with file_path.open("w", encoding="utf-8") as f:
                f.write(tabulate(data, headers="keys", tablefmt="grid"))
            click.secho(f"✓ Table results saved to {file_path}", fg="green")

    except PermissionError:
        click.secho(
            f"✗ Permission denied: Cannot write to {filename}", fg="red", err=True
        )
    except OSError as e:
        click.secho(f"✗ OS error while saving results: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"✗ Failed to save results: {e}", fg="red", err=True)


def format_dns_record(
    results: list[dict], style: str = "standard", *, show_ttl: bool = False
) -> list[dict]:
    """Format DNS records in different styles."""
    formatted: list[dict[str, str]] = []

    for result in results:
        if style == "short":
            for rtype, data in result["records"].items():
                records = data.get("records", [])
                for record in records:
                    transformed_list: list[dict[str, str]] = []
                    transformed_list.extend(
                        [
                            {
                                "domain": result["domain"],
                                "type": rtype,
                                "value": record,
                            }
                            for result in results
                            for rtype, records in result["records"].items()
                            for record in records
                        ]
                    )
        else:
            row: dict[str, str] = {"domain": result["domain"]}
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


def format_dns_trace(trace_result: dict) -> list[dict[str, Any]]:
    """Format DNS trace results."""
    formatted: list[dict[str, int | str | None]] = []

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

    final: dict[str, str] | None = trace_result.get("final_answer")
    if final and final not in hops:
        response_time: str | None = final.get("response_time")
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


def format_dns_comparison(comparison_result: dict) -> list[dict]:
    """Format DNS comparison results."""
    formatted: list[dict[str, int | str]] = []

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


def format_dns_health(health_result: dict) -> list[dict]:
    """Format DNS health check results."""
    formatted: list[dict[str, str | int | None]] = [
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
