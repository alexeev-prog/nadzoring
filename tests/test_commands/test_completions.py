import pathlib
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from nadzoring.commands.completions_commands import (
    _SOURCE_POWERSHELL,
    PowerShellComplete,
    _generate_completion_script,
    _get_root_cli_and_prog_name,
    completion_group,
)


class TestPowerShellComplete:
    def test_name_attribute(self):
        assert PowerShellComplete.name == "powershell"

    def test_source_template(self):
        assert PowerShellComplete.source_template == _SOURCE_POWERSHELL

    def test_func_name_with_hyphens(self):
        completer = PowerShellComplete(
            cli=MagicMock(),
            ctx_args={},
            prog_name="my-app-name",
            complete_var="TEST_VAR",
        )
        assert completer.func_name == "my_app_name"

    def test_func_name_without_hyphens(self):
        completer = PowerShellComplete(cli=MagicMock(), ctx_args={}, prog_name="myapp", complete_var="TEST_VAR")
        assert completer.func_name == "myapp"

    def test_func_name_empty(self):
        completer = PowerShellComplete(cli=MagicMock(), ctx_args={}, prog_name="", complete_var="TEST_VAR")
        assert completer.func_name == ""


class TestGetRootCliAndProgName:
    def test_single_level_context(self):
        cli = click.Group(name="test")
        ctx = click.Context(cli, info_name="testcli")

        root_cli, prog_name = _get_root_cli_and_prog_name(ctx)

        assert root_cli is cli
        assert prog_name == "testcli"

    def test_multi_level_context(self):
        grandparent_cli = click.Group(name="grandparent")
        parent_cli = click.Group(name="parent")
        child_cli = click.Command(name="child")

        grandparent_cli.add_command(parent_cli)
        parent_cli.add_command(child_cli)

        grandparent_ctx = click.Context(grandparent_cli, info_name="grandparent")
        parent_ctx = click.Context(parent_cli, parent=grandparent_ctx, info_name="parent")
        child_ctx = click.Context(child_cli, parent=parent_ctx, info_name="child")

        root_cli, prog_name = _get_root_cli_and_prog_name(child_ctx)

        assert root_cli is grandparent_cli
        assert prog_name == "grandparent"

    def test_info_name_none_defaults_to_nadzoring(self):
        cli = click.Group()
        ctx = click.Context(cli)

        root_cli, prog_name = _get_root_cli_and_prog_name(ctx)

        assert root_cli is cli
        assert prog_name == "nadzoring"


class TestGenerateCompletionScript:
    def test_bash_shell(self):
        cli = click.Group(name="test")
        script = _generate_completion_script("bash", cli, "testprog")

        assert "_TESTPROG_COMPLETE=bash_complete" in script
        assert "complete" in script
        assert "testprog" in script
        assert "_testprog_completion" in script

    def test_zsh_shell(self):
        cli = click.Group(name="test")
        script = _generate_completion_script("zsh", cli, "testprog")

        assert "#compdef testprog" in script
        assert "_TESTPROG_COMPLETE=zsh_complete" in script

    def test_fish_shell(self):
        cli = click.Group(name="test")
        script = _generate_completion_script("fish", cli, "testprog")

        assert "function _testprog_completion" in script
        assert "complete" in script
        assert "testprog" in script

    def test_powershell_shell(self):
        cli = click.Group(name="test")
        script = _generate_completion_script("powershell", cli, "testprog")

        assert "Register-ArgumentCompleter" in script
        assert "testprog" in script
        assert "_TESTPROG_COMPLETE" in script

    def test_unsupported_shell_raises_error(self):
        cli = click.Group(name="test")

        with pytest.raises(click.UsageError) as exc_info:
            _generate_completion_script("unsupported", cli, "testprog")

        assert "Shell 'unsupported' is not supported" in str(exc_info.value)
        assert "bash, zsh, fish, powershell" in str(exc_info.value)

    def test_prog_name_with_hyphens_sanitized_in_var(self):
        cli = click.Group(name="test")
        script = _generate_completion_script("bash", cli, "test-prog-name")

        assert "_TEST_PROG_NAME_COMPLETE" in script


class TestCompletionGroupCommands:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_completion_bash(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["bash"])

            assert result.exit_code == 0
            assert "_NADZORING_COMPLETE=bash_complete" in result.output
            assert "complete" in result.output
            assert "nadzoring" in result.output
            assert "_nadzoring_completion" in result.output

    def test_completion_zsh(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["zsh"])

            assert result.exit_code == 0
            assert "#compdef nadzoring" in result.output
            assert "_NADZORING_COMPLETE=zsh_complete" in result.output

    def test_completion_fish(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["fish"])

            assert result.exit_code == 0
            assert "function _nadzoring_completion" in result.output
            assert "complete" in result.output
            assert "nadzoring" in result.output

    def test_completion_powershell(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["powershell"])

            assert result.exit_code == 0
            assert "Register-ArgumentCompleter" in result.output
            assert "CommandName nadzoring" in result.output
            assert "_NADZORING_COMPLETE" in result.output

    @patch("nadzoring.commands.completions_commands._generate_completion_script")
    @patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name")
    def test_completion_bash_calls_generate_script(self, mock_get, mock_generate, runner):
        mock_cli = click.Group(name="nadzoring")
        mock_get.return_value = (mock_cli, "nadzoring")
        mock_generate.return_value = "mock script"

        result = runner.invoke(completion_group, ["bash"])

        assert result.exit_code == 0
        assert result.output == "mock script"
        mock_generate.assert_called_once_with("bash", mock_cli, "nadzoring")

    @patch("nadzoring.commands.completions_commands._generate_completion_script")
    @patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name")
    def test_completion_zsh_calls_generate_script(self, mock_get, mock_generate, runner):
        mock_cli = click.Group(name="nadzoring")
        mock_get.return_value = (mock_cli, "nadzoring")
        mock_generate.return_value = "mock script"

        result = runner.invoke(completion_group, ["zsh"])

        assert result.exit_code == 0
        assert result.output == "mock script"
        mock_generate.assert_called_once_with("zsh", mock_cli, "nadzoring")

    @patch("nadzoring.commands.completions_commands._generate_completion_script")
    @patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name")
    def test_completion_fish_calls_generate_script(self, mock_get, mock_generate, runner):
        mock_cli = click.Group(name="nadzoring")
        mock_get.return_value = (mock_cli, "nadzoring")
        mock_generate.return_value = "mock script"

        result = runner.invoke(completion_group, ["fish"])

        assert result.exit_code == 0
        assert result.output == "mock script"
        mock_generate.assert_called_once_with("fish", mock_cli, "nadzoring")

    @patch("nadzoring.commands.completions_commands._generate_completion_script")
    @patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name")
    def test_completion_powershell_calls_generate_script(self, mock_get, mock_generate, runner):
        mock_cli = click.Group(name="nadzoring")
        mock_get.return_value = (mock_cli, "nadzoring")
        mock_generate.return_value = "mock script"

        result = runner.invoke(completion_group, ["powershell"])

        assert result.exit_code == 0
        assert result.output == "mock script"
        mock_generate.assert_called_once_with("powershell", mock_cli, "nadzoring")


class TestCompletionHintsCommand:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_completion_hints_bash(self, runner):
        result = runner.invoke(completion_group, ["hints", "bash"])

        assert result.exit_code == 0
        assert "Bash Installation Hints:" in result.output
        assert 'eval "$(nadzoring completion bash)"' in result.output
        assert "~/.bashrc" in result.output

    def test_completion_hints_zsh(self, runner):
        result = runner.invoke(completion_group, ["hints", "zsh"])

        assert result.exit_code == 0
        assert "Zsh Installation Hints:" in result.output
        assert 'eval "$(nadzoring completion zsh)"' in result.output
        assert "~/.zshrc" in result.output
        assert "fpath" in result.output

    def test_completion_hints_fish(self, runner):
        result = runner.invoke(completion_group, ["hints", "fish"])

        assert result.exit_code == 0
        assert "Fish Installation Hints:" in result.output
        assert "nadzoring completion fish | source" in result.output
        assert ".config/fish/completions" in result.output

    def test_completion_hints_powershell(self, runner):
        result = runner.invoke(completion_group, ["hints", "powershell"])

        assert result.exit_code == 0
        assert "PowerShell Installation Hints:" in result.output
        assert "Invoke-Expression" in result.output
        assert "$PROFILE" in result.output

    def test_completion_hints_invalid_shell(self, runner):
        result = runner.invoke(completion_group, ["hints", "invalid"])

        assert result.exit_code == 2
        assert "Invalid value" in result.output or "Error:" in result.output

    def test_completion_hints_help_message(self, runner):
        result = runner.invoke(completion_group, ["hints", "--help"])

        assert result.exit_code == 0
        assert "Display installation hints" in result.output


class TestIntegration:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_complete_flow_bash(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["bash"])
            assert result.exit_code == 0

            with runner.isolated_filesystem():
                pathlib.Path("completion.bash").write_text(result.output)

                with pathlib.Path("completion.bash").open() as f:
                    content = f.read()
                    assert "_NADZORING_COMPLETE" in content
                    assert "complete" in content
                    assert "nadzoring" in content

    def test_complete_flow_powershell(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result = runner.invoke(completion_group, ["powershell"])
            assert result.exit_code == 0

            assert "Register-ArgumentCompleter" in result.output
            assert "CommandName nadzoring" in result.output

    def test_multiple_completion_calls_independent(self, runner):
        with patch("nadzoring.commands.completions_commands._get_root_cli_and_prog_name") as mock_get:
            mock_cli = click.Group(name="nadzoring")
            mock_get.return_value = (mock_cli, "nadzoring")

            result1 = runner.invoke(completion_group, ["bash"])
            result2 = runner.invoke(completion_group, ["zsh"])

            assert result1.exit_code == 0
            assert result2.exit_code == 0
            assert result1.output != result2.output
            assert "bash_complete" in result1.output
            assert "zsh_complete" in result2.output

    def test_completion_group_help(self, runner):
        result = runner.invoke(completion_group, ["--help"])

        assert result.exit_code == 0
        assert "Generate shell completion scripts" in result.output
        assert "bash" in result.output
        assert "zsh" in result.output
        assert "fish" in result.output
        assert "powershell" in result.output
        assert "hints" in result.output
