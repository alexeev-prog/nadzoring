"""Parse and dispatch interactive commands through the existing CLI."""

import shlex
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

import click

from nadzoring.shell.completion import _output_choices
from nadzoring.shell.terminal import shell_input


@dataclass
class ShellSession:
    """Interactive command dispatcher with a session-local output default.

    ``command`` is the existing root Click group. ``output`` is the session
    default, or None to use normal CLI defaults.
    """

    command: click.Group
    output: str | None = None

    def execute(self, line: str) -> bool:
        """Execute one shell line, returning False only for exit or quit.

        Args:
            line: Command line with shell-style quoting (not shell expansion).

        Returns:
            Whether the interactive session should continue.
        """
        try:
            args = shlex.split(line)
            return self._dispatch(args)
        except ValueError as error:
            click.echo(f"Error: {error}", err=True)
        except click.ClickException as error:
            error.show()
        except (click.Abort, KeyboardInterrupt):
            click.echo("Aborted!", err=True)
        return True

    def _dispatch(self, args: list[str]) -> bool:
        """Handle shell built-ins or invoke Click without terminating the process."""
        if not args:
            return True
        if args[0] in {"exit", "quit", "clear"}:
            if len(args) != 1:
                raise click.UsageError(f"{args[0]} does not accept arguments.")
            if args[0] == "clear":
                click.clear()
                return True
            return False
        if args[0] == "set":
            return self._set_output(args)
        if args[0] == "help":
            args = [*args[1:], "--help"]
        if any(arg in {"-i", "--interactive"} for arg in args[:1]):
            raise click.UsageError("Already in an interactive shell.")
        self.command.main(
            args=args,
            prog_name="nadzoring",
            standalone_mode=False,
            default_map=self._defaults(self.command),
            obj={"interactive_shell": True},
        )
        return True

    def _set_output(self, args: list[str]) -> bool:
        """Validate output using the same choices as the CLI."""
        choices = _output_choices(self.command)
        if len(args) != 3 or args[1] != "output" or args[2] not in choices:
            raise click.UsageError(f"Usage: set output {{{'|'.join(choices)}}}")
        self.output = args[2]
        return True

    def _defaults(self, command: click.Command) -> dict[str, Any]:
        """Build nested Click defaults without changing command definitions."""
        defaults: dict[str, Any] = {}
        if self.output is not None and any(param.name == "output" for param in command.params):
            defaults["output"] = self.output
        if isinstance(command, click.Group):
            defaults.update({name: self._defaults(child) for name, child in command.commands.items()})
        return defaults


# Click option callbacks receive their boolean value positionally.
def start_interactive(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Start the shell for Click's eager interactive option.

    Args:
        ctx: Root Click context.
        _param: Interactive option definition.
        value: Whether the option was supplied.
    """
    if not value or ctx.resilient_parsing:
        return
    if ctx.obj and ctx.obj.get("interactive_shell"):
        raise click.UsageError("Already in an interactive shell.")
    command = ctx.command
    if not isinstance(command, click.Group):
        raise TypeError("The interactive shell requires a Click group.")
    session = ShellSession(command)
    click.echo(f"nadzoring v{version('nadzoring')} | type 'help' for commands, 'exit' to quit")
    with shell_input(command) as read_line:
        while True:
            try:
                line = read_line()
            except EOFError:
                click.echo()
                break
            except KeyboardInterrupt:
                click.echo()
                continue
            if not session.execute(line):
                break
    ctx.exit()
