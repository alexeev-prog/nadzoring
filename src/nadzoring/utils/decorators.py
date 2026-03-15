"""Common decorators for CLI commands."""

import functools
import json
from collections.abc import Callable
from time import time
from types import SimpleNamespace
from typing import Any, TypeVar, cast

import click

from nadzoring.logger import setup_cli_logging
from nadzoring.utils.formatters import (
    print_csv_table,
    print_html_table,
    print_results_table,
    save_results,
)

F = TypeVar("F", bound=Callable[..., Any])


def common_cli_options(
    *,
    include_verbose: bool = False,
    include_quiet: bool = False,
    include_no_color: bool = False,
    include_output: bool = False,
    include_save: bool = False,
) -> Callable[[F], F]:
    """
    Decorator factory that adds common CLI options to click commands.

    This decorator provides standardized CLI options across all commands,
    with selective inclusion based on the command's needs. It handles:
    - Logging configuration (verbose/quiet modes)
    - Output format selection (table, json, csv, html)
    - Result saving to files
    - Performance timing in verbose mode

    Args:
        include_verbose: If True, pass verbose flag to the wrapped function.
            Defaults to False.
        include_quiet: If True, pass quiet flag to the wrapped function.
            Defaults to False.
        include_no_color: If True, pass no_color flag to the wrapped function.
            Defaults to False.
        include_output: If True, pass output format to the wrapped function.
            Defaults to False.
        include_save: If True, pass save path to the wrapped function.
            Defaults to False.

    Returns:
        A decorator function that wraps a click command with common options.

    Example:
        @click.command()
        @common_cli_options(include_verbose=True)
        def my_command(verbose: bool) -> None:
            '''My command implementation.'''
            if verbose:
                click.echo("Running in verbose mode")

    """

    def decorator(func: F) -> F:
        """Apply common CLI options decorators to the function."""
        decorated_func: F = func
        decorated_func = click.option("--verbose", is_flag=True, help="Verbose output (DEBUG level)")(decorated_func)
        decorated_func = click.option("--quiet", is_flag=True, help="Quiet mode (no logs, only results)")(
            decorated_func
        )
        decorated_func = click.option("--no-color", is_flag=True, help="Disable colored output")(decorated_func)
        decorated_func = click.option(
            "--output",
            "-o",
            type=click.Choice(["table", "json", "csv", "html", "html_table"]),
            default="table",
            help="Output format",
        )(decorated_func)
        decorated_func = click.option("--save", type=click.Path(), help="Save results to file")(decorated_func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that handles CLI options and output formatting.

            Args:
                *args: Variable positional arguments passed to the wrapped function.
                **kwargs: Variable keyword arguments passed to the wrapped function.

            Returns:
                The result of the wrapped function.

            """
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

        return cast(F, wrapper)

    return decorator


def _extract_cli_options(kwargs: dict[str, Any]) -> SimpleNamespace:
    """
    Extract CLI options from function keyword arguments.

    This function removes CLI-specific options from the kwargs dictionary
    and returns them as a SimpleNamespace object.

    Args:
        kwargs: Dictionary of keyword arguments passed to the wrapped function.

    Returns:
        SimpleNamespace containing extracted CLI options with default values
        for any missing options.

    """
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
    """
    Filter which CLI options are passed to the wrapped function.

    Based on the include flags, this function selectively adds CLI options
    to the keyword arguments that will be passed to the wrapped function.

    Args:
        kwargs: Original keyword arguments dictionary.
        cli_options: SimpleNamespace containing extracted CLI options.
        include_verbose: Whether to include the verbose option.
        include_quiet: Whether to include the quiet option.
        include_no_color: Whether to include the no_color option.
        include_output: Whether to include the output option.
        include_save: Whether to include the save option.

    Returns:
        Filtered dictionary of keyword arguments for the wrapped function.

    """
    func_kwargs: dict[str, Any] = kwargs.copy()

    option_mappings: list[tuple[bool, str, Any]] = [
        (include_verbose, "verbose", cli_options.verbose),
        (include_quiet, "quiet", cli_options.quiet),
        (include_no_color, "no_color", cli_options.no_color),
        (include_output, "output", cli_options.output),
        (include_save, "save", cli_options.save),
    ]

    filtered_options: dict[str, Any] = {name: value for include, name, value in option_mappings if include}

    func_kwargs.update(filtered_options)
    return func_kwargs


def _setup_logging(cli_options: SimpleNamespace) -> None:
    """
    Configure logging based on CLI options.

    Sets up logging with appropriate verbosity, quiet mode, and color settings.

    Args:
        cli_options: SimpleNamespace containing CLI options with verbose,
                    quiet, and no_color attributes.

    """
    setup_cli_logging(
        verbose=cli_options.verbose,
        quiet=cli_options.quiet,
        no_color=cli_options.no_color,
    )


def _handle_output(result: Any, output_format: str, *, no_color: bool) -> None:
    """
    Display command results in the requested format.

    Args:
        result: The result data from the command to display.
        output_format: The output format to use (json, table, csv, html, html_table).
        no_color: If True, disable colored output in table formatting.

    Raises:
        click.ClickException: If there's an error processing the output format.

    """
    try:
        if output_format == "json":
            click.echo(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        elif output_format == "table":
            print_results_table(result, no_color=no_color)
        elif output_format == "csv":
            print_csv_table(result)
        elif output_format in {"html", "html_table"}:
            print_html_table(result, full_page=(output_format == "html"))
    except Exception as e:
        raise click.ClickException(f"Error displaying output: {e}") from e


def _handle_save(result: Any, save_path: str | None, output_format: str) -> None:
    """
    Save command results to a file if a save path is provided.

    Args:
        result: The result data from the command to save.
        save_path: Path where the results should be saved, or None if not saving.
        output_format: The output format to use for saving.

    Raises:
        click.ClickException: If there's an error saving the file.

    """
    if save_path:
        try:
            save_results(result, save_path, output_format)
        except Exception as e:
            raise click.ClickException(f"Error saving results to {save_path}: {e}") from e


def _show_completion_time(elapsed: float, *, verbose: bool) -> None:
    """
    Display command completion time in verbose mode.

    Args:
        elapsed: Time elapsed in seconds since command started.
        verbose: If True, display the completion time.

    """
    if verbose:
        click.secho(f"\n⚡ Completed in {elapsed:.2f} seconds", dim=True)
