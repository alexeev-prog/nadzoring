"""Prompt toolkit adapter, loaded only when the optional dependency is available."""

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style

from nadzoring.shell.completion import BUILTINS, completion_items

SHELL_STYLE = Style.from_dict({
    "command": "ansicyan bold",
    "option": "ansiyellow",
    "string": "ansigreen",
    "number": "ansimagenta",
})
_TOKENS = re.compile(r"""\s+|(?:[^\s'"\\]|\\(?:.|$)|'[^']*(?:'|$)|"(?:[^"\\]|\\.)*(?:"|$))+""")


class ShellLexer(Lexer):
    """Highlight commands, options, strings, and numbers without a parser dependency."""

    def __init__(self, command: click.Group) -> None:
        """Collect command names from the existing Click tree."""
        self.commands = set(BUILTINS)
        pending = [command]
        while pending:
            group = pending.pop()
            self.commands.update(group.commands)
            pending.extend(child for child in group.commands.values() if isinstance(child, click.Group))

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        """Return styled fragments, including unfinished quotes while editing."""

        def get_line(number: int) -> StyleAndTextTuples:
            if number >= len(document.lines):
                return []
            return [(self._style(match.group()), match.group()) for match in _TOKENS.finditer(document.lines[number])]

        return get_line

    def _style(self, token: str) -> str:
        """Classify one shell token without changing its text."""
        if token in self.commands:
            return "class:command"
        if token.startswith(("'", '"')):
            return "class:string"
        try:
            float(token)
        except ValueError:
            return "class:option" if token.startswith("-") else ""
        return "class:number"


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
        items, incomplete = completion_items(self.command, document.text_before_cursor)
        for item in items:
            if item.type in {"file", "dir"}:
                paths = PathCompleter(only_directories=item.type == "dir")
                yield from paths.get_completions(Document(incomplete), complete_event)
            else:
                yield Completion(item.value, start_position=-len(incomplete), display_meta=item.help or "")


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
        lexer=ShellLexer(command),
        style=SHELL_STYLE,
        complete_while_typing=True,
    )
    yield lambda: session.prompt("nadzoring> ")
