"""Regression tests for interactive dispatch, completion, and terminal backends."""

import importlib
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import click
import pytest
from click.testing import CliRunner

from nadzoring.cli import cli
from nadzoring.shell.completion import _output_choices, complete_line
from nadzoring.shell.session import ShellSession, start_interactive
from nadzoring.shell import terminal
from nadzoring.utils.decorators import common_cli_options


@pytest.fixture
def command():
    @click.group()
    def root():
        pass

    @root.group()
    def nested():
        pass

    @nested.command()
    @common_cli_options()
    @click.argument("value")
    def echo(value):
        return [{"value": value}]

    @root.command()
    def abort():
        raise click.Abort()

    return root


def test_session_dispatch_defaults_override_and_save(command, tmp_path, capsys):
    session = ShellSession(command)
    assert session.execute("set output json")
    target = tmp_path / "quoted file.json"
    assert session.execute(f'nested echo "two words" --save "{target}"')
    assert '"value": "two words"' in capsys.readouterr().out
    assert '"two words"' in target.read_text()
    assert session.execute("nested echo other -o csv")
    assert "value" in capsys.readouterr().out
    assert session.output == "json"
    assert ShellSession(command).output is None


@pytest.mark.parametrize("line", ["", "  ", "help", "help nested", "help nested echo", "nested echo --help"])
def test_help_and_empty_input(command, line):
    assert ShellSession(command).execute(line)


@pytest.mark.parametrize(
    "line, message",
    [
        ('nested echo "', "No closing quotation"),
        ("missing", "No such command"),
        ("nested echo", "Missing argument"),
        ("set output invalid", "Usage: set output"),
        ("set", "Usage: set output"),
        ("exit extra", "does not accept arguments"),
        ("--interactive", "Already in an interactive shell"),
        ("abort", "Aborted!"),
    ],
)
def test_errors_keep_session_alive(command, line, message, capsys):
    assert ShellSession(command).execute(line)
    assert message in capsys.readouterr().err


@pytest.mark.parametrize("line", ["exit", "quit"])
def test_exit(command, line):
    assert not ShellSession(command).execute(line)


def test_clear_and_keyboard_interrupt(command, monkeypatch):
    clear = MagicMock()
    monkeypatch.setattr(click, "clear", clear)
    session = ShellSession(command)
    assert session.execute("clear")
    clear.assert_called_once()
    monkeypatch.setattr(command, "main", MagicMock(side_effect=KeyboardInterrupt))
    assert session.execute("nested echo x")


@pytest.mark.parametrize(
    "line, expected, partial",
    [
        ("dn", "dns", "dn"),
        ("dns re", "resolve", "re"),
        ("dns resolve --out", "--output", "--out"),
        ("dns resolve --output j", "json", "j"),
        ("help dns re", "resolve", "re"),
        ("set o", "output", "o"),
        ("set output j", "json", "j"),
        ("", "exit", ""),
    ],
)
def test_completion(line, expected, partial):
    values, incomplete = complete_line(cli, line)
    assert expected in values
    assert incomplete == partial


def test_output_choices_without_options():
    assert _output_choices(click.Group()) == []
    group = click.Group(commands={"empty": click.Command("empty")})
    group.params.append(click.Option(["--other"]))
    assert _output_choices(group) == []


def test_completion_covers_existing_command_tree():
    def check(group, path):
        values, _ = complete_line(cli, " ".join(path) + (" " if path else ""))
        for name, child in group.commands.items():
            assert name in values
            child_path = [*path, name]
            if isinstance(child, click.Group):
                check(child, child_path)
            else:
                options, _ = complete_line(cli, " ".join(child_path) + " --")
                for param in child.params:
                    if isinstance(param, click.Option):
                        for option in param.opts:
                            if option.startswith("--"):
                                assert option in options

    check(cli, [])


def test_real_command_with_session_output_and_explicit_override(capsys):
    session = ShellSession(cli)
    assert session.execute("set output json")
    assert session.execute("network-base parse-url https://example.com/path")
    assert '"' in capsys.readouterr().out
    assert session.execute("network-base parse-url https://example.com/path --output csv")
    assert "example.com" in capsys.readouterr().out


def test_real_cli_dispatch(monkeypatch, capsys):
    session = ShellSession(cli)
    assert session.execute("dns resolve --help")
    assert "--output" in capsys.readouterr().out
    assert session.execute("-i")
    # A later eager flag cannot recursively enter a shell either.
    assert session.execute("--help -i")


@pytest.mark.parametrize("flag", ["-i", "--interactive"])
def test_interactive_entrypoint(flag, monkeypatch):
    events = iter([KeyboardInterrupt(), "help dns", "exit"])

    @contextmanager
    def reader(_command):
        def read():
            value = next(events)
            if isinstance(value, BaseException):
                raise value
            return value

        yield read

    monkeypatch.setattr("nadzoring.shell.session.shell_input", reader)
    result = CliRunner().invoke(cli, [flag])
    assert result.exit_code == 0, result.output
    assert "nadzoring v" in result.output
    assert "resolve" in result.output


def test_entrypoint_eof(monkeypatch):
    @contextmanager
    def reader(_command):
        yield MagicMock(side_effect=EOFError)

    monkeypatch.setattr("nadzoring.shell.session.shell_input", reader)
    assert CliRunner().invoke(cli, ["-i"]).exit_code == 0


def test_banner_uses_package_version(monkeypatch):
    @contextmanager
    def reader(_command):
        yield lambda: "exit"

    monkeypatch.setattr("nadzoring.shell.session.shell_input", reader)
    package_version = MagicMock(return_value="9.8.7")
    monkeypatch.setattr("nadzoring.shell.session.version", package_version)
    result = CliRunner().invoke(cli, ["-i"])
    assert result.exit_code == 0
    assert "nadzoring v9.8.7 | type 'help' for commands, 'exit' to quit" in result.output
    package_version.assert_called_once_with("nadzoring")


def test_eager_callback_guards():
    param = click.Option(["-i"])
    context = click.Context(cli, resilient_parsing=True)
    start_interactive(context, param, True)
    start_interactive(context, param, False)
    with pytest.raises(click.UsageError, match="Already"):
        start_interactive(click.Context(cli, obj={"interactive_shell": True}), param, True)
    with pytest.raises(TypeError, match="requires a Click group"):
        start_interactive(click.Context(click.Command("test")), param, True)


def test_load_history_errors(tmp_path, capsys):
    assert terminal._load_history(tmp_path / "missing") == []
    assert terminal._load_history(tmp_path) == []
    assert "cannot read" in capsys.readouterr().err
    invalid = tmp_path / "invalid"
    invalid.write_bytes(b"\xff")
    assert terminal._load_history(invalid) == []


@pytest.mark.parametrize("backend", ["bare", "readline", "toolkit"])
def test_history_persistence_and_backend_selection(backend, command, tmp_path, monkeypatch):
    history_path = tmp_path / ".nadzoring_history"
    history_path.write_text("previous\n")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    imports = importlib.import_module
    readline = MagicMock()
    readline.__doc__ = "libedit"
    readline.get_current_history_length.return_value = 1
    readline.get_history_item.return_value = "original"
    readline.get_line_buffer.return_value = "nested e"
    readline.get_endidx.return_value = len("nested e")
    monkeypatch.setattr("builtins.input", lambda _prompt: "nested echo x")

    @contextmanager
    def toolkit_reader(_command, history):
        assert history == ["previous"]
        yield lambda: "nested echo x"

    def load(name):
        if name.endswith("toolkit"):
            if backend != "toolkit":
                raise ImportError
            return type("Toolkit", (), {"toolkit_input": staticmethod(toolkit_reader)})
        if name == "readline":
            if backend == "bare":
                raise ImportError
            return readline
        return imports(name)

    monkeypatch.setattr(terminal, "import_module", load)
    with terminal.shell_input(command) as read:
        assert read() == "nested echo x"
        if backend == "readline":
            completer = readline.set_completer.call_args_list[0].args[0]
            assert completer("e", 0) == "echo"
            assert completer("e", 10) is None
    assert history_path.read_text() == "previous\nnested echo x\n"
    if backend == "readline":
        readline.add_history.assert_any_call("original")


def test_history_write_error_and_blank_lines(command, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "missing-directory")
    monkeypatch.setattr(terminal, "import_module", MagicMock(side_effect=ImportError))
    inputs = iter([" ", "help"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    with terminal.shell_input(command) as read:
        assert read() == " "
        assert read() == "help"
    assert capsys.readouterr().err.count("cannot save") == 1


def test_toolkit_adapter(monkeypatch):
    pytest.importorskip("prompt_toolkit")
    from prompt_toolkit.document import Document
    from prompt_toolkit.completion import CompleteEvent
    from nadzoring.shell.toolkit import ClickCompleter, toolkit_input

    results = list(ClickCompleter(cli).get_completions(Document("dns re"), CompleteEvent()))
    assert any(item.text == "resolve" and item.start_position == -2 for item in results)
    prompt = MagicMock()
    prompt.return_value.prompt.return_value = "help"
    monkeypatch.setattr("nadzoring.shell.toolkit.PromptSession", prompt)
    with toolkit_input(cli, ["previous"]) as read:
        assert read() == "help"
