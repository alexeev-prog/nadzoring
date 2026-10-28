"""Interactive completion backed by Click's existing command tree."""

import click
from click.shell_completion import CompletionItem, ShellComplete, split_arg_string

BUILTINS = ("help", "exit", "quit", "clear", "set")


def complete_line(command: click.Group, text: str) -> tuple[list[str], str]:
    """Return completion candidates and the partial word before the cursor.

    Args:
        command: Root CLI group.
        text: Input before the cursor, including any trailing whitespace.

    Returns:
        Candidate values and the word they replace.
    """
    items, incomplete = completion_items(command, text)
    return [item.value for item in items], incomplete


def completion_items(command: click.Group, text: str) -> tuple[list[CompletionItem], str]:
    """Return Click candidates with descriptions and the replacement suffix.

    Args:
        command: Root CLI group.
        text: Input before the cursor.

    Returns:
        Completion items and the partial value to replace.
    """
    args = split_arg_string(text)
    incomplete = args.pop() if args and not text.endswith((" ", "\t")) else ""
    if args[:1] == ["set"]:
        choices = ["output"] if len(args) == 1 else _output_choices(command) if args == ["set", "output"] else []
        return [CompletionItem(value) for value in choices if value.startswith(incomplete)], incomplete
    if args[:1] == ["help"]:
        args = args[1:]
    backend = ShellComplete(command, {}, "nadzoring", "_NADZORING_COMPLETE")
    items = backend.get_completions(args, incomplete)
    if incomplete.startswith("-") and "=" in incomplete:
        incomplete = incomplete.partition("=")[2]
    if not args:
        items.extend(CompletionItem(value) for value in BUILTINS if value.startswith(incomplete))
    unique = {item.value: item for item in items}
    return [unique[value] for value in sorted(unique)], incomplete


def _output_choices(command: click.Command) -> list[str]:
    """Find output formats in the existing Click option definitions."""
    for param in command.params:
        if param.name == "output" and isinstance(param.type, click.Choice):
            return list(param.type.choices)
    if isinstance(command, click.Group):
        for child in command.commands.values():
            if choices := _output_choices(child):
                return choices
    return []
