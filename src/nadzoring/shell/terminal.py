"""Optional terminal backends with a shared, plain-text command history."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path

import click

from nadzoring.shell.completion import complete_line


def _load_history(path: Path) -> list[str]:
    """Read history without making an inaccessible home directory fatal."""
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError) as error:
        click.echo(f"Warning: cannot read shell history: {error}", err=True)
        return []


@contextmanager
def _fallback_input(command: click.Group, history: list[str]) -> Iterator[Callable[[], str]]:
    """Configure readline when available, otherwise use bare input."""
    try:
        readline = import_module("readline")
    except ImportError:
        yield lambda: input("nadzoring> ")
        return
    previous = readline.get_completer()
    delimiters = readline.get_completer_delims()
    saved_history = [readline.get_history_item(index) for index in range(1, readline.get_current_history_length() + 1)]

    def complete(_text: str, state: int) -> str | None:
        values, incomplete = complete_line(command, readline.get_line_buffer()[: readline.get_endidx()])
        prefix = _text[: len(_text) - len(incomplete)]
        return prefix + values[state] if state < len(values) else None

    readline.clear_history()
    for line in history:
        readline.add_history(line)
    readline.set_completer(complete)
    readline.set_completer_delims(" \t\n")
    readline.parse_and_bind("bind ^I rl_complete" if "libedit" in (readline.__doc__ or "") else "tab: complete")
    try:
        yield lambda: input("nadzoring> ")
    finally:
        readline.set_completer(previous)
        readline.set_completer_delims(delimiters)
        readline.clear_history()
        for line in saved_history:
            readline.add_history(line)


@contextmanager
def shell_input(command: click.Group) -> Iterator[Callable[[], str]]:
    """Provide a line reader with completion and persistent history.

    Args:
        command: Root Click group used for completion.

    Yields:
        A callable prompting for the next command line.
    """
    path = Path.home() / ".nadzoring_history"
    history = _load_history(path)
    try:
        toolkit = import_module("nadzoring.shell.toolkit")
    except ImportError:
        backend = _fallback_input(command, history)
    else:
        backend = toolkit.toolkit_input(command, history)
    with backend as read_line:

        def read_and_save() -> str:
            line = read_line()
            if line.strip():
                try:
                    # Keep files private on creation; append to preserve concurrent sessions.
                    path.touch(mode=0o600, exist_ok=True)
                    with path.open("a", encoding="utf-8") as stream:
                        stream.write(line + "\n")
                except OSError as error:
                    click.echo(f"Warning: cannot save shell history: {error}", err=True)
            return line

        yield read_and_save
