"""Common decorators for CLI commands."""

import functools
import json
import socket
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from time import time
from types import SimpleNamespace
from typing import Any, TypeVar, cast

import click
import socks
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
_DEFAULT_LIFETIME_TIMEOUT: float = 30.0


@dataclass(frozen=True)
class _CliOptionSpec:
    """Descriptor for a single injectable CLI option group."""

    flag: str
    kwarg: str
    click_options: tuple[Any, ...]
    extractor: Callable[[dict[str, Any]], Any]
    default: Any


def _make_timeout_config(kwargs: dict[str, Any]) -> TimeoutConfig:
    """Pop timeout-related kwargs and build a TimeoutConfig."""
    lifetime: float | None = kwargs.pop("timeout", None)
    connect: float | None = kwargs.pop("connect_timeout", None)
    read: float | None = kwargs.pop("read_timeout", None)

    return TimeoutConfig(
        connect=(connect if connect is not None else (lifetime if lifetime is not None else _DEFAULT_CONNECT_TIMEOUT)),
        read=(read if read is not None else (lifetime if lifetime is not None else _DEFAULT_READ_TIMEOUT)),
        lifetime=lifetime if lifetime is not None else _DEFAULT_LIFETIME_TIMEOUT,
    )


def _parse_proxy_url(proxy_url: str) -> tuple[str, str, int]:
    """
    Parse proxy URL and return (proxy_type, host, port).

    Supported formats:
    - socks5://host:port
    - socks4://host:port
    - http://host:port
    - https://host:port

    Args:
        proxy_url: Proxy URL string.

    Returns:
        Tuple of (proxy_type, host, port).

    Raises:
        ValueError: If proxy URL format is invalid.
    """
    if not proxy_url or "://" not in proxy_url:
        raise ValueError(f"Invalid proxy URL format: {proxy_url}")

    protocol, rest = proxy_url.split("://", 1)
    protocol = protocol.lower()

    if protocol not in {"socks5", "socks4", "http", "https"}:
        raise ValueError(f"Unsupported proxy protocol: {protocol}. Supported: socks5, socks4, http, https")

    if ":" in rest:
        host, port_str = rest.split(":", 1)
        port_str = port_str.strip()
        if not port_str:
            port = 1080 if protocol.startswith("socks") else 8080
        else:
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise ValueError(f"Port out of range: {port}")  # noqa: TRY301
            except ValueError:
                port = 1080 if protocol.startswith("socks") else 8080
    else:
        host = rest
        port = 1080 if protocol.startswith("socks") else 8080

    if not host:
        raise ValueError(f"Missing host in proxy URL: {proxy_url}")

    return protocol, host, port


def _setup_global_proxy(proxy: str | None) -> None:
    """
    Setup global proxy for all socket connections.

    Supports SOCKS4, SOCKS5, HTTP, HTTPS proxies.
    This patches the socket module globally.

    Args:
        proxy: Proxy URL (e.g., 'socks5://host:port', 'http://host:port') or None to disable.
    """
    if not proxy:
        if hasattr(socket, "_original_socket"):
            socket.socket = socket._original_socket  # type: ignore  # noqa: SLF001
        return

    try:
        protocol, host, port = _parse_proxy_url(proxy)

        if protocol == "socks5":
            socks.set_default_proxy(socks.SOCKS5, host, port)
            socket.socket = socks.socksocket  # type: ignore
        elif protocol == "socks4":
            socks.set_default_proxy(socks.SOCKS4, host, port)
            socket.socket = socks.socksocket  # type: ignore
        elif protocol in {"http", "https"}:
            proxy_handler = urllib.request.ProxyHandler({
                "http": f"http://{host}:{port}",
                "https": f"https://{host}:{port}",
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
    except Exception as e:
        raise click.ClickException(f"Failed to setup proxy '{proxy}': {e}") from e


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
    _CliOptionSpec(
        flag="include_proxy",
        kwarg="proxy",
        click_options=(
            click.option(
                "--proxy",
                type=str,
                help="Proxy URL (e.g., 'socks5://127.0.0.1:1080', 'http://proxy:8080')",
            ),
        ),
        extractor=lambda kw: kw.pop("proxy", None),
        default=None,
    ),
)

_REGISTRY_BY_FLAG: dict[str, _CliOptionSpec] = {spec.flag: spec for spec in _OPTION_REGISTRY}

_ALWAYS_EXTRACTED: frozenset[str] = frozenset({"verbose", "quiet", "no_color", "output", "save", "proxy"})


def common_cli_options(**enabled_flags: bool) -> Callable[[F], F]:
    """Decorator factory that adds common CLI options to click commands."""
    unknown = set(enabled_flags) - _REGISTRY_BY_FLAG.keys()
    if unknown:
        raise ValueError(f"Unknown common_cli_options flags: {unknown}")

    active_specs: tuple[_CliOptionSpec, ...] = tuple(spec for spec in _OPTION_REGISTRY if enabled_flags.get(spec.flag))

    def decorator(func: F) -> F:
        decorated_func: F = func

        for spec in _OPTION_REGISTRY:
            if enabled_flags.get(spec.flag) or spec.kwarg in _ALWAYS_EXTRACTED:
                for click_opt in reversed(spec.click_options):
                    decorated_func = click_opt(decorated_func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            extracted: dict[str, Any] = {
                spec.kwarg: spec.extractor(kwargs)
                for spec in _OPTION_REGISTRY
                if enabled_flags.get(spec.flag) or spec.kwarg in _ALWAYS_EXTRACTED
            }

            cli_opts = SimpleNamespace(
                verbose=extracted["verbose"],
                quiet=extracted["quiet"],
                no_color=extracted["no_color"],
                output=extracted["output"],
                save=extracted["save"],
                proxy=extracted["proxy"],
            )

            func_kwargs: dict[str, Any] = {
                **kwargs,
                **{spec.kwarg: extracted[spec.kwarg] for spec in active_specs},
            }

            _setup_logging(cli_opts)

            proxy = extracted.get("proxy")
            if proxy:
                _setup_global_proxy(proxy)

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
    """Configure logging based on CLI options."""
    setup_cli_logging(
        verbose=cli_options.verbose,
        quiet=cli_options.quiet,
        no_color=cli_options.no_color,
    )


def _handle_output(result: Any, output_format: str, *, no_color: bool) -> None:
    """Render command results in the requested format."""
    output_handlers: dict[str, Callable[[], None]] = {
        "json": lambda: click.echo(json.dumps(result, indent=2, default=str, ensure_ascii=False)),
        "yaml": lambda: click.echo(
            yaml.dump(
                result,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=120,
            )
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
    """Persist command results to a file when a path is provided."""
    if save_path is None:
        return

    try:
        save_results(result, save_path, output_format)
    except Exception as e:
        raise click.ClickException(f"Error saving results to {save_path}: {e}") from e


def _show_completion_time(elapsed: float, *, verbose: bool) -> None:
    """Print elapsed time when verbose mode is active."""
    if verbose:
        click.secho(f"\n⚡ Completed in {elapsed:.2f} seconds", dim=True)
