"""Common decorators for CLI commands."""

import functools
import json
from collections.abc import Callable
from dataclasses import dataclass
from time import time
from types import SimpleNamespace
from typing import Any, TypeVar, cast

import click
import yaml

from nadzoring.logger import setup_cli_logging
from nadzoring.utils.formatters import (
    print_csv_table,
    print_html_table,
    print_results_table,
    save_results,
)
from nadzoring.utils.timeout import TimeoutConfig

F = TypeVar("F", bound=Callable[..., Any])

_DEFAULT_CONNECT_TIMEOUT: float = 5.0
_DEFAULT_READ_TIMEOUT: float = 10.0


@dataclass(frozen=True)
class _CliOptionSpec:
    """Descriptor for a single injectable CLI option group.

    Adding a new option to the decorator requires only a new entry in
    ``_OPTION_REGISTRY`` — nothing else in this file changes.

    Attributes:
        flag: Keyword argument name for ``common_cli_options``,
            e.g. ``"include_verbose"``.
        kwarg: Parameter name injected into the wrapped function,
            e.g. ``"verbose"``.
        click_options: Click option decorators that register the underlying
            CLI flags.  May be empty when the injected value is synthesised
            from multiple raw flags (e.g. ``timeout_config``).
        extractor: ``(kwargs) -> value`` — pops the relevant keys from the
            raw kwargs dict and returns the value to inject.
        default: Value used when the option group is disabled.
    """

    flag: str
    kwarg: str
    click_options: tuple[Any, ...]
    extractor: Callable[[dict[str, Any]], Any]
    default: Any


def _make_timeout_config(kwargs: dict[str, Any]) -> TimeoutConfig:
    """Pop timeout-related kwargs and build a TimeoutConfig.

    Resolution order for ``connect`` and ``read``:
    1. Explicit ``--connect-timeout`` / ``--read-timeout``.
    2. Generic ``--timeout`` (lifetime fallback for both phases).
    3. Module-level defaults.

    Args:
        kwargs: Mutable dict from the wrapper call.

    Returns:
        Fully populated TimeoutConfig.

    """
    lifetime: float | None = kwargs.pop("timeout", None)
    connect: float | None = kwargs.pop("connect_timeout", None)
    read: float | None = kwargs.pop("read_timeout", None)

    return TimeoutConfig(
        connect=connect if connect is not None else (lifetime or _DEFAULT_CONNECT_TIMEOUT),
        read=read if read is not None else (lifetime or _DEFAULT_READ_TIMEOUT),
        lifetime=lifetime,
    )


_OPTION_REGISTRY: tuple[_CliOptionSpec, ...] = (
    _CliOptionSpec(
        flag="include_verbose",
        kwarg="verbose",
        click_options=(click.option("--verbose", is_flag=True, help="Verbose output (DEBUG level)"),),
        extractor=lambda kw: kw.pop("verbose", False),
        default=False,
    ),
    _CliOptionSpec(
        flag="include_quiet",
        kwarg="quiet",
        click_options=(click.option("--quiet", is_flag=True, help="Quiet mode (no logs, only results)"),),
        extractor=lambda kw: kw.pop("quiet", False),
        default=False,
    ),
    _CliOptionSpec(
        flag="include_no_color",
        kwarg="no_color",
        click_options=(click.option("--no-color", is_flag=True, help="Disable colored output"),),
        extractor=lambda kw: kw.pop("no_color", False),
        default=False,
    ),
    _CliOptionSpec(
        flag="include_output",
        kwarg="output",
        click_options=(
            click.option(
                "--output",
                "-o",
                type=click.Choice(["table", "json", "csv", "html", "html_table", "yaml"]),
                default="table",
                help="Output format",
            ),
        ),
        extractor=lambda kw: kw.pop("output", "table"),
        default="table",
    ),
    _CliOptionSpec(
        flag="include_save",
        kwarg="save",
        click_options=(click.option("--save", type=click.Path(), help="Save results to file"),),
        extractor=lambda kw: kw.pop("save", None),
        default=None,
    ),
    _CliOptionSpec(
        flag="include_timeout",
        kwarg="timeout_config",
        click_options=(
            click.option(
                "--timeout",
                type=float,
                default=None,
                help="Lifetime timeout for the entire operation (seconds).",
            ),
            click.option(
                "--connect-timeout",
                type=float,
                default=None,
                help=f"Connection timeout (seconds). Falls back to --timeout, then {_DEFAULT_CONNECT_TIMEOUT}.",
            ),
            click.option(
                "--read-timeout",
                type=float,
                default=None,
                help=f"Read timeout (seconds). Falls back to --timeout, then {_DEFAULT_READ_TIMEOUT}.",
            ),
        ),
        extractor=_make_timeout_config,
        default=None,
    ),
)

_REGISTRY_BY_FLAG: dict[str, _CliOptionSpec] = {spec.flag: spec for spec in _OPTION_REGISTRY}

_ALWAYS_EXTRACTED: frozenset[str] = frozenset({"verbose", "quiet", "no_color", "output", "save"})


def common_cli_options(**enabled_flags: bool) -> Callable[[F], F]:
    """Decorator factory that adds common CLI options to click commands.

    Pass any subset of the known ``include_*`` flags as keyword arguments.
    Unknown flag names raise ``ValueError`` at decoration time.

    Known flags (see ``_OPTION_REGISTRY`` for the authoritative list):
        ``include_verbose``, ``include_quiet``, ``include_no_color``,
        ``include_output``, ``include_save``, ``include_timeout``.

    Args:
        **enabled_flags: Mapping of ``include_<name>`` → ``bool``.
            Omitted flags default to ``False``.

    Returns:
        A decorator that wraps a click command with the requested options.

    Raises:
        ValueError: If an unknown flag name is supplied.

    Example:
        @click.command()
        @common_cli_options(include_verbose=True, include_timeout=True)
        def port_scan(verbose: bool, timeout_config: TimeoutConfig) -> dict:
            ...

    """
    unknown = set(enabled_flags) - _REGISTRY_BY_FLAG.keys()
    if unknown:
        raise ValueError(f"Unknown common_cli_options flags: {unknown}")

    active_specs: tuple[_CliOptionSpec, ...] = tuple(spec for spec in _OPTION_REGISTRY if enabled_flags.get(spec.flag))

    def decorator(func: F) -> F:
        decorated_func: F = func

        for spec in _OPTION_REGISTRY:
            for click_opt in reversed(spec.click_options):
                decorated_func = click_opt(decorated_func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract every registered option so no unexpected kwargs leak into
            # the real function.
            extracted: dict[str, Any] = {spec.kwarg: spec.extractor(kwargs) for spec in _OPTION_REGISTRY}

            cli_opts = SimpleNamespace(
                verbose=extracted["verbose"],
                quiet=extracted["quiet"],
                no_color=extracted["no_color"],
                output=extracted["output"],
                save=extracted["save"],
            )

            # Forward only explicitly requested options to the wrapped function.
            func_kwargs: dict[str, Any] = {**kwargs, **{spec.kwarg: extracted[spec.kwarg] for spec in active_specs}}

            _setup_logging(cli_opts)

            start: float = time()
            result = func(*args, **func_kwargs)
            elapsed: float = time() - start

            _handle_output(result, cli_opts.output, no_color=cli_opts.no_color)
            _handle_save(result, cli_opts.save, cli_opts.output)
            _show_completion_time(elapsed, verbose=cli_opts.verbose)

            return result

        return cast(F, wrapper)

    return decorator


def _setup_logging(cli_options: SimpleNamespace) -> None:
    """Configure logging based on CLI options.

    Args:
        cli_options: Namespace with ``verbose``, ``quiet``, ``no_color``.

    """
    setup_cli_logging(
        verbose=cli_options.verbose,
        quiet=cli_options.quiet,
        no_color=cli_options.no_color,
    )


def _handle_output(result: Any, output_format: str, *, no_color: bool) -> None:
    """Render command results in the requested format.

    Args:
        result: Data returned by the command.
        output_format: One of ``json``, ``yaml``, ``table``, ``csv``,
            ``html``, ``html_table``.
        no_color: Disable ANSI colours in table output.

    Raises:
        click.ClickException: On any rendering error.

    """
    output_handlers: dict[str, Callable[[], None]] = {
        "json": lambda: click.echo(json.dumps(result, indent=2, default=str, ensure_ascii=False)),
        "yaml": lambda: click.echo(
            yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2, width=120)
        ),
        "table": lambda: print_results_table(result, no_color=no_color),
        "csv": lambda: print_csv_table(result),
        "html": lambda: print_html_table(result, full_page=True),
        "html_table": lambda: print_html_table(result, full_page=False),
    }

    try:
        handler = output_handlers.get(output_format)
        if handler is not None:
            handler()
    except Exception as e:
        raise click.ClickException(f"Error displaying output: {e}") from e


def _handle_save(result: Any, save_path: str | None, output_format: str) -> None:
    """Persist command results to a file when a path is provided.

    Args:
        result: Data returned by the command.
        save_path: Destination path, or ``None`` to skip.
        output_format: Format used when serialising.

    Raises:
        click.ClickException: On any I/O error.

    """
    if save_path is None:
        return

    try:
        save_results(result, save_path, output_format)
    except Exception as e:
        raise click.ClickException(f"Error saving results to {save_path}: {e}") from e


def _show_completion_time(elapsed: float, *, verbose: bool) -> None:
    """Print elapsed time when verbose mode is active.

    Args:
        elapsed: Seconds since the command started.
        verbose: Emit the timing line only when ``True``.

    """
    if verbose:
        click.secho(f"\n⚡ Completed in {elapsed:.2f} seconds", dim=True)
