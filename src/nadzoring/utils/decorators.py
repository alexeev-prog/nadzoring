# src/nadzoring/cli/utils/decorators.py
"""Common decorators for CLI commands."""

import functools
import json
from collections.abc import Callable
from time import time
from types import SimpleNamespace
from typing import Any

import click

from nadzoring.logger import setup_cli_logging
from nadzoring.utils.formatters import (
    print_csv_table,
    print_html_table,
    print_results_table,
    save_results,
)


def common_cli_options(
    *,
    include_verbose: bool = False,
    include_quiet: bool = False,
    include_no_color: bool = False,
    include_output: bool = False,
    include_save: bool = False,
) -> Callable:
    """Common CLI options for all commands with selective inclusion."""

    def decorator[F: Callable[..., Any]](func: F) -> F:
        decorated_func = func
        decorated_func = click.option(
            "--verbose", is_flag=True, help="Verbose output (DEBUG level)"
        )(decorated_func)
        decorated_func = click.option(
            "--quiet", is_flag=True, help="Quiet mode (no logs, only results)"
        )(decorated_func)
        decorated_func = click.option(
            "--no-color", is_flag=True, help="Disable colored output"
        )(decorated_func)
        decorated_func = click.option(
            "--output",
            "-o",
            type=click.Choice(["table", "json", "csv", "html", "html_table"]),
            default="table",
            help="Output format",
        )(decorated_func)
        decorated_func = click.option(
            "--save", type=click.Path(), help="Save results to file"
        )(decorated_func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cli_options: SimpleNamespace = _extract_cli_options(kwargs)

            func_kwargs: dict[str, Any] = _filter_func_kwargs(
                kwargs,
                cli_options,
                include_verbose=include_verbose,
                include_quiet=include_quiet,
                include_no_color=include_no_color,
                include_output=include_output,
                include_save=include_save,
            )

            _setup_logging(cli_options)

            start_time: float = time()
            result = func(*args, **func_kwargs)
            elapsed: float = time() - start_time

            _handle_output(result, cli_options.output, no_color=cli_options.no_color)

            _handle_save(result, cli_options.save, cli_options.output)

            _show_completion_time(elapsed, verbose=cli_options.verbose)

            return result

        return wrapper

    return decorator


def _extract_cli_options(kwargs: dict[str, Any]) -> SimpleNamespace:
    """Extract CLI options from kwargs."""
    return SimpleNamespace(
        verbose=kwargs.pop("verbose", False),
        quiet=kwargs.pop("quiet", False),
        no_color=kwargs.pop("no_color", False),
        output=kwargs.pop("output", "table"),
        save=kwargs.pop("save", None),
    )


def _filter_func_kwargs(
    kwargs: dict[str, Any],
    cli_options: SimpleNamespace,
    *,
    include_verbose: bool,
    include_quiet: bool,
    include_no_color: bool,
    include_output: bool,
    include_save: bool,
) -> dict[str, Any]:
    """Filter which CLI options get passed to the wrapped function."""
    func_kwargs: dict[str, Any] = kwargs.copy()

    filtered_options: dict[str, Any] = {
        name: value
        for include, name, value in [
            (include_verbose, "verbose", cli_options.verbose),
            (include_quiet, "quiet", cli_options.quiet),
            (include_no_color, "no_color", cli_options.no_color),
            (include_output, "output", cli_options.output),
            (include_save, "save", cli_options.save),
        ]
        if include
    }

    func_kwargs.update(filtered_options)
    return func_kwargs


def _setup_logging(cli_options: SimpleNamespace) -> None:
    """Setup logging based on CLI options."""
    setup_cli_logging(
        verbose=cli_options.verbose,
        quiet=cli_options.quiet,
        no_color=cli_options.no_color,
    )


def _handle_output(result: Any, output_format: str, *, no_color: bool) -> None:
    """Handle different output formats."""
    if output_format == "json":
        click.echo(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    elif output_format == "table":
        print_results_table(result, no_color=no_color)
    elif output_format == "csv":
        print_csv_table(result)
    elif output_format in {"html", "html_table"}:
        print_html_table(result, full_page=(output_format == "html"))


def _handle_save(result: Any, save_path: str | None, output_format: str) -> None:
    """Handle saving results to file if requested."""
    if save_path:
        save_results(result, save_path, output_format)


def _show_completion_time(elapsed: float, *, verbose: bool) -> None:
    """Show completion time if verbose mode is enabled."""
    if verbose:
        click.secho(f"\n⚡ Completed in {elapsed:.2f} seconds", dim=True)
