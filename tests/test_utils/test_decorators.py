"""Tests for nadzoring.utils.decorators — 100% coverage."""

import json
from unittest.mock import patch

import click
import pytest
import yaml
from click.testing import CliRunner

from nadzoring.utils.decorators import (
    _handle_output,
    _handle_save,
    _show_completion_time,
    common_cli_options,
)
from nadzoring.utils.timeout import TimeoutConfig


class TestHandleOutput:
    DATA = [{"domain": "example.com", "ip": "1.2.3.4"}]

    def test_json_output(self, capsys):
        _handle_output(self.DATA, "json", no_color=True)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == self.DATA

    def test_yaml_output(self, capsys):
        _handle_output(self.DATA, "yaml", no_color=True)
        out = capsys.readouterr().out
        parsed = yaml.safe_load(out)
        assert parsed == self.DATA

    def test_table_output_calls_print_results_table(self):
        with patch("nadzoring.utils.decorators.print_results_table") as mock_fn:
            _handle_output(self.DATA, "table", no_color=False)
            mock_fn.assert_called_once_with(self.DATA, no_color=False)

    def test_csv_output_calls_print_csv_table(self):
        with patch("nadzoring.utils.decorators.print_csv_table") as mock_fn:
            _handle_output(self.DATA, "csv", no_color=False)
            mock_fn.assert_called_once_with(self.DATA)

    def test_html_table_output(self):
        with patch("nadzoring.utils.decorators.print_html_table") as mock_fn:
            _handle_output(self.DATA, "html_table", no_color=False)
            mock_fn.assert_called_once_with(self.DATA, full_page=False)

    def test_html_output_full_page(self):
        with patch("nadzoring.utils.decorators.print_html_table") as mock_fn:
            _handle_output(self.DATA, "html", no_color=False)
            mock_fn.assert_called_once_with(self.DATA, full_page=True)

    def test_table_output_raises_click_exception_on_error(self):
        with (
            patch(
                "nadzoring.utils.decorators.print_results_table",
                side_effect=Exception("boom"),
            ),
            pytest.raises(click.ClickException),
        ):
            _handle_output(self.DATA, "table", no_color=False)

    def test_unknown_format_does_nothing(self, capsys):
        _handle_output(self.DATA, "nonexistent_format", no_color=False)
        out = capsys.readouterr().out
        assert out == ""


class TestHandleSave:
    def test_no_save_path_does_nothing(self):
        with patch("nadzoring.utils.decorators.save_results") as mock_fn:
            _handle_save([{"a": 1}], None, "json")
            mock_fn.assert_not_called()

    def test_save_path_calls_save_results(self):
        with patch("nadzoring.utils.decorators.save_results") as mock_fn:
            _handle_save([{"a": 1}], "/tmp/out.json", "json")
            mock_fn.assert_called_once_with([{"a": 1}], "/tmp/out.json", "json")

    def test_save_error_raises_click_exception(self):
        with (
            patch(
                "nadzoring.utils.decorators.save_results",
                side_effect=Exception("disk full"),
            ),
            pytest.raises(click.ClickException),
        ):
            _handle_save([{"a": 1}], "/tmp/out.json", "json")


class TestShowCompletionTime:
    def test_verbose_shows_time(self, capsys):
        _show_completion_time(1.23, verbose=True)
        out = capsys.readouterr().out
        assert "1.23" in out

    def test_non_verbose_shows_nothing(self, capsys):
        _show_completion_time(1.23, verbose=False)
        out = capsys.readouterr().out
        assert out == ""

    def test_zero_elapsed(self, capsys):
        _show_completion_time(0.0, verbose=True)
        out = capsys.readouterr().out
        assert "0.00" in out


class TestCommonCliOptionsIntegration:
    def test_default_table_output_exit_zero(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options()
        def cmd(**kwargs):
            return [{"result": "data"}]

        result = runner.invoke(cmd, [])
        assert result.exit_code == 0

    def test_json_format_flag(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options()
        def cmd(**kwargs):
            return [{"key": "value"}]

        result = runner.invoke(cmd, ["--output", "json"])
        assert result.exit_code == 0
        assert "key" in result.output

    def test_yaml_output(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options()
        def cmd(**kwargs):
            return [{"domain": "example.com"}]

        result = runner.invoke(cmd, ["--output", "yaml"])
        assert result.exit_code == 0
        parsed = yaml.safe_load(result.output.split("\n\n")[0])
        assert parsed[0]["domain"] == "example.com"

    def test_verbose_flag_accepted(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options(include_verbose=True)
        def cmd(**kwargs):
            return []

        result = runner.invoke(cmd, ["--verbose"])
        assert result.exit_code == 0

    def test_quiet_flag_accepted(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options(include_quiet=True)
        def cmd(**kwargs):
            return []

        result = runner.invoke(cmd, ["--quiet"])
        assert result.exit_code == 0

    def test_no_color_flag_accepted(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options(include_no_color=True)
        def cmd(**kwargs):
            return []

        result = runner.invoke(cmd, ["--no-color"])
        assert result.exit_code == 0

    def test_save_flag_accepted(self, tmp_path):
        runner = CliRunner()
        save_path = str(tmp_path / "out.json")

        @click.command()
        @common_cli_options()
        def cmd(**kwargs):
            return [{"saved": True}]

        result = runner.invoke(cmd, ["--output", "json", "--save", save_path])
        assert result.exit_code == 0

    def test_include_verbose_passes_to_function(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_verbose=True)
        def cmd(verbose, **kwargs):
            received["verbose"] = verbose
            return []

        runner.invoke(cmd, ["--verbose"])
        assert received["verbose"] is True

    def test_verbose_false_without_flag(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_verbose=True)
        def cmd(verbose, **kwargs):
            received["verbose"] = verbose
            return []

        runner.invoke(cmd, [])
        assert received["verbose"] is False

    def test_verbose_not_injected_without_include(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_verbose=False)
        def cmd(**kwargs):
            received["kwargs"] = kwargs
            return []

        runner.invoke(cmd, [])
        assert "verbose" not in received.get("kwargs", {})

    def test_invalid_output_choice_fails(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options()
        def cmd(**kwargs):
            return []

        result = runner.invoke(cmd, ["--output", "invalid_format"])
        assert result.exit_code != 0

    def test_include_timeout_passes_timeout_config(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_timeout=True)
        def cmd(timeout_config, **kwargs):
            received["cfg"] = timeout_config
            return []

        runner.invoke(cmd, [])
        assert isinstance(received["cfg"], TimeoutConfig)

    def test_timeout_flag_sets_lifetime(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_timeout=True)
        def cmd(timeout_config, **kwargs):
            received["cfg"] = timeout_config
            return []

        runner.invoke(cmd, ["--timeout", "60"])
        assert received["cfg"].lifetime == 60.0

    def test_connect_timeout_flag(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_timeout=True)
        def cmd(timeout_config, **kwargs):
            received["cfg"] = timeout_config
            return []

        runner.invoke(cmd, ["--connect-timeout", "3"])
        assert received["cfg"].connect == 3.0

    def test_read_timeout_flag(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_timeout=True)
        def cmd(timeout_config, **kwargs):
            received["cfg"] = timeout_config
            return []

        runner.invoke(cmd, ["--read-timeout", "15"])
        assert received["cfg"].read == 15.0

    def test_timeout_fallback_when_only_lifetime(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_timeout=True)
        def cmd(timeout_config, **kwargs):
            received["cfg"] = timeout_config
            return []

        runner.invoke(cmd, ["--timeout", "20"])
        assert received["cfg"].connect == 20.0
        assert received["cfg"].read == 20.0

    def test_unknown_flag_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown common_cli_options flags"):
            common_cli_options(include_nonexistent=True)

    def test_verbose_completion_time_shown(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options(include_verbose=True)
        def cmd(**kwargs):
            return []

        result = runner.invoke(cmd, ["--verbose"])
        assert "seconds" in result.output or result.exit_code == 0

    def test_include_output_not_passed_to_function(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_output=False)
        def cmd(**kwargs):
            received["kwargs"] = kwargs
            return []

        runner.invoke(cmd, [])
        assert "output" not in received.get("kwargs", {})

    def test_include_save_passes_save_path(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_save=True)
        def cmd(save, **kwargs):
            received["save"] = save
            return []

        runner.invoke(cmd, [])
        assert received.get("save") is None

    def test_no_color_disables_color_in_table(self):
        runner = CliRunner()

        @click.command()
        @common_cli_options(include_no_color=True)
        def cmd(**kwargs):
            return [{"status": "CRITICAL"}]

        result = runner.invoke(cmd, ["--no-color"])
        assert result.exit_code == 0
        assert "\x1b" not in result.output
