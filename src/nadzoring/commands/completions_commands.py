"""Shell completion support for the nadzoring CLI.

Provides completion commands for bash, zsh, fish, and PowerShell shells.
Each shell has its own dedicated command that emits the appropriate shell
integration script.

Typical usage (end-user):
    nadzoring completion bash >> ~/.bashrc
    nadzoring completion zsh >> ~/.zshrc
    nadzoring completion fish > ~/.config/fish/completions/nadzoring.fish
    nadzoring completion powershell >> $PROFILE
"""

from __future__ import annotations

import click
from click.shell_completion import (
    ShellComplete,
    add_completion_class,
    get_completion_class,
)

_SOURCE_POWERSHELL: str = """\
Register-ArgumentCompleter -Native -CommandName %(prog_name)s -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $env:%(complete_var)s = "powershell_complete"
    $env:COMP_WORDS = $commandAst.ToString()
    $env:COMP_CWORD = $commandAst.CommandElements.Count - 1
    $completions = & %(prog_name)s
    $env:%(complete_var)s = ""
    $completions | ForEach-Object {
        $parts = $_ -split ","
        if ($parts[0] -eq "plain") {
            [System.Management.Automation.CompletionResult]::new(
                $parts[1], $parts[1],
                [System.Management.Automation.CompletionResultType]::ParameterValue,
                $parts[1]
            )
        }
    }
}
"""


class PowerShellComplete(ShellComplete):
    """Click completion backend for PowerShell (pwsh / Windows PowerShell).

    Registered under the "powershell" shell name so that Click's env-var
    dispatch mechanism can route completion requests correctly.

    Attributes:
        name: Shell identifier used as the command name.
        source_template: Template string for the integration snippet.
    """

    name = "powershell"
    source_template = _SOURCE_POWERSHELL

    @property
    def func_name(self) -> str:
        """Returns a PowerShell-safe function/variable name.

        Replaces hyphens with underscores so the generated snippet is valid
        PowerShell syntax regardless of the program name.

        Returns:
            Sanitised program name suitable for PowerShell identifiers.
        """
        return self.prog_name.replace("-", "_")


# Register the custom PowerShell completion class
add_completion_class(PowerShellComplete, name="powershell")


def _get_root_cli_and_prog_name(ctx: click.Context) -> tuple[click.BaseCommand, str]:
    """Retrieves the root CLI command and program name from the context.

    Args:
        ctx: Click context object containing command information.

    Returns:
        A tuple containing (root_command, program_name).
    """
    root_ctx = ctx
    while root_ctx.parent is not None:
        root_ctx = root_ctx.parent

    root_cli: click.BaseCommand = root_ctx.command
    prog_name: str = root_ctx.info_name or "nadzoring"
    return root_cli, prog_name


def _generate_completion_script(
    shell: str,
    cli: click.BaseCommand,
    prog_name: str,
) -> str:
    """Generates the shell integration script for the specified shell.

    Args:
        shell: Target shell name (bash, zsh, fish, or powershell).
        cli: Root Click command group of the application.
        prog_name: Binary name as invoked by the user.

    Returns:
        The complete shell script as a string.

    Raises:
        click.UsageError: If the specified shell is unsupported.
    """
    completion_class = get_completion_class(shell)
    if completion_class is None:
        raise click.UsageError(f"Shell '{shell}' is not supported. Supported shells: bash, zsh, fish, powershell")

    complete_var: str = f"_{prog_name.upper().replace('-', '_')}_COMPLETE"
    completer = completion_class(cli, {}, prog_name, complete_var)  # type: ignore[arg-type]
    return completer.source()


@click.group(name="completion")
def completion_group() -> None:
    """Generate shell completion scripts for various shells.

    Each subcommand outputs a shell-specific completion script that can be
    sourced or saved to enable tab-completion for the nadzoring CLI.
    """


@completion_group.command(name="bash")
@click.pass_context
def completion_bash(ctx: click.Context) -> None:
    """Generate bash completion script.

    Examples:
        eval "$(nadzoring completion bash)"
        or
        nadzoring completion bash > ~/.nadzoring-complete.bash
        echo 'source ~/.nadzoring-complete.bash' >> ~/.bashrc
    """
    root_cli, prog_name = _get_root_cli_and_prog_name(ctx)
    script = _generate_completion_script("bash", root_cli, prog_name)
    click.echo(script, nl=False)


@completion_group.command(name="zsh")
@click.pass_context
def completion_zsh(ctx: click.Context) -> None:
    """Generate zsh completion script.

    Examples:
        eval "$(nadzoring completion zsh)"
        or
        nadzoring completion zsh > "${fpath[1]}/_nadzoring"
    """
    root_cli, prog_name = _get_root_cli_and_prog_name(ctx)
    script = _generate_completion_script("zsh", root_cli, prog_name)
    click.echo(script, nl=False)


@completion_group.command(name="fish")
@click.pass_context
def completion_fish(ctx: click.Context) -> None:
    """Generate fish completion script.

    Examples:
        nadzoring completion fish | source
        or
        nadzoring completion fish > ~/.config/fish/completions/nadzoring.fish
    """
    root_cli, prog_name = _get_root_cli_and_prog_name(ctx)
    script = _generate_completion_script("fish", root_cli, prog_name)
    click.echo(script, nl=False)


@completion_group.command(name="powershell")
@click.pass_context
def completion_powershell(ctx: click.Context) -> None:
    """Generate PowerShell completion script.

    Examples:
        nadzoring completion powershell | Invoke-Expression
        or
        nadzoring completion powershell >> $PROFILE
    """
    root_cli, prog_name = _get_root_cli_and_prog_name(ctx)
    script = _generate_completion_script("powershell", root_cli, prog_name)
    click.echo(script, nl=False)


@completion_group.command(name="hints")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish", "powershell"]))
def completion_hints(shell: str) -> None:
    """Display installation hints for the specified shell.

    Shows detailed instructions on how to install and enable completions
    for the given shell.

    Args:
        shell: The shell to show hints for (bash, zsh, fish, or powershell).
    """
    hints = {
        "bash": """
Bash Installation Hints:
-----------------------
Option 1 (recommended):
    echo 'eval "$(nadzoring completion bash)"' >> ~/.bashrc
    source ~/.bashrc

Option 2 (persistent file):
    nadzoring completion bash > ~/.nadzoring-complete.bash
    echo 'source ~/.nadzoring-complete.bash' >> ~/.bashrc

Note: On macOS, use ~/.bash_profile instead of ~/.bashrc
        """,
        "zsh": """
Zsh Installation Hints:
----------------------
Option 1 (recommended):
    echo 'eval "$(nadzoring completion zsh)"' >> ~/.zshrc
    source ~/.zshrc

Option 2 (using fpath):
    nadzoring completion zsh > "${fpath[1]}/_nadzoring"
    # Then add to ~/.zshrc:
    echo 'autoload -U compinit && compinit' >> ~/.zshrc
        """,
        "fish": """
Fish Installation Hints:
-----------------------
Option 1 (temporary):
    nadzoring completion fish | source

Option 2 (permanent):
    nadzoring completion fish > ~/.config/fish/completions/nadzoring.fish
    # Completions will be loaded automatically on shell startup
        """,
        "powershell": """
PowerShell Installation Hints:
----------------------------
Option 1 (current session):
    nadzoring completion powershell | Invoke-Expression

Option 2 (permanent - add to profile):
    nadzoring completion powershell >> $PROFILE
    # Reload profile:
    . $PROFILE

Note: $PROFILE path varies by PowerShell version and configuration.
      Run '$PROFILE' to see your profile path.
        """,
    }

    hint = hints.get(shell.lower(), "No hints available for this shell.")
    click.echo(hint)
