"""Prompt toolkit adapter, loaded only when the optional dependency is available."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from nadzoring.shell.completion import complete_line


class ClickCompleter(Completer):
    """Adapt the Click command tree to prompt toolkit completions."""

    def __init__(self, command: click.Group) -> None:
        """Store the root Click group for completion requests."""
        self.command = command

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterator[Completion]:
        """Yield Click candidates replacing the current incomplete word.

        Args:
            document: Current input and cursor position.
            complete_event: Prompt toolkit completion event.

        Yields:
            Completion candidates for the current cursor position.
        """
        values, incomplete = complete_line(self.command, document.text_before_cursor)
        for value in values:
            yield Completion(value, start_position=-len(incomplete))


@contextmanager
def toolkit_input(command: click.Group, history: list[str]) -> Iterator[Callable[[], str]]:
    """Create a prompt toolkit session with the shared history.

    Args:
        command: Root Click group for completion.
        history: Previously persisted command lines.

    Yields:
        A callable prompting for the next command line.
    """
    session: PromptSession[str] = PromptSession(
        completer=ClickCompleter(command),
        history=InMemoryHistory(history),
    )
    yield lambda: session.prompt("nadzoring> ")
