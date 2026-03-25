"""Tests for nadzoring.utils.decorators."""

import json
from types import SimpleNamespace
from unittest.mock import patch

import click
import pytest
import yaml
from click.testing import CliRunner

from nadzoring.utils.decorators import (
    _extract_cli_options,
    _filter_func_kwargs,
    _handle_output,
    _handle_save,
    _show_completion_time,
    common_cli_options,
)

# ---------------------------------------------------------------------------
# _extract_cli_options
# ---------------------------------------------------------------------------


class TestExtractCliOptions:
    def test_extracts_all_options(self):
        kwargs = {
            "verbose": True,
            "quiet": False,
            "no_color": True,
            "output": "json",
            "save": "/tmp/out.json",
        }
        opts = _extract_cli_options(kwargs)
        assert opts.verbose is True
        assert opts.quiet is False
        assert opts.no_color is True
        assert opts.output == "json"
        assert opts.save == "/tmp/out.json"

    def test_removes_options_from_kwargs(self):
        kwargs = {
            "verbose": True,
            "quiet": False,
            "no_color": False,
            "output": "table",
            "save": None,
            "custom": 42,
        }
        _extract_cli_options(kwargs)
        assert "verbose" not in kwargs
        assert "quiet" not in kwargs
        assert "no_color" not in kwargs
        assert "output" not in kwargs
        assert "save" not in kwargs
        assert "custom" in kwargs

    def test_defaults_when_missing(self):
        kwargs = {}
        opts = _extract_cli_options(kwargs)
        assert opts.verbose is False
        assert opts.quiet is False
        assert opts.no_color is False
        assert opts.output == "table"
        assert opts.save is None


# ---------------------------------------------------------------------------
# _filter_func_kwargs
# ---------------------------------------------------------------------------


class TestFilterFuncKwargs:
    def _opts(self, **overrides):
        defaults = {
            "verbose": True,
            "quiet": False,
            "no_color": True,
            "output": "json",
            "save": "/out",
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_includes_verbose_when_flag_set(self):
        result = _filter_func_kwargs(
            {},
            self._opts(),
            include_verbose=True,
            include_quiet=False,
            include_no_color=False,
            include_output=False,
            include_save=False,
        )
        assert result["verbose"] is True

    def test_excludes_verbose_when_flag_false(self):
        result = _filter_func_kwargs(
            {},
            self._opts(),
            include_verbose=False,
            include_quiet=False,
            include_no_color=False,
            include_output=False,
            include_save=False,
        )
        assert "verbose" not in result

    def test_includes_all_flags(self):
        result = _filter_func_kwargs(
            {},
            self._opts(),
            include_verbose=True,
            include_quiet=True,
            include_no_color=True,
            include_output=True,
            include_save=True,
        )
        assert "verbose" in result
        assert "quiet" in result
        assert "no_color" in result
        assert "output" in result
        assert "save" in result

    def test_passthrough_kwargs_preserved(self):
        kwargs = {"my_param": "hello"}
        result = _filter_func_kwargs(
            kwargs,
            self._opts(),
            include_verbose=False,
            include_quiet=False,
            include_no_color=False,
            include_output=False,
            include_save=False,
        )
        assert result["my_param"] == "hello"

    def test_does_not_mutate_original_kwargs(self):
        kwargs = {"param": "value"}
        original = dict(kwargs)
        _filter_func_kwargs(
            kwargs,
            self._opts(),
            include_verbose=True,
            include_quiet=False,
            include_no_color=False,
            include_output=False,
            include_save=False,
        )
        assert kwargs == original


# ---------------------------------------------------------------------------
# _handle_output
# ---------------------------------------------------------------------------


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

    def test_invalid_output_format_raises_click_exception(self):
        with (
            patch(
                "nadzoring.utils.decorators.print_results_table",
                side_effect=Exception("boom"),
            ),
            pytest.raises(click.ClickException),
        ):
            _handle_output(self.DATA, "table", no_color=False)


# ---------------------------------------------------------------------------
# _handle_save
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# _show_completion_time
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# common_cli_options integration
# ---------------------------------------------------------------------------


class TestCommonCliOptionsIntegration:
    def _make_command(self, **decorator_kwargs):
        @click.command()
        @common_cli_options(**decorator_kwargs)
        def cmd(**kwargs):
            click.echo("ok")
            return [{"result": "data"}]

        return cmd

    def test_default_table_output(self):
        runner = CliRunner()
        cmd = self._make_command()
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

    def test_verbose_flag_accepted(self):
        runner = CliRunner()
        cmd = self._make_command(include_verbose=True)
        result = runner.invoke(cmd, ["--verbose"])
        assert result.exit_code == 0

    def test_quiet_flag_accepted(self):
        runner = CliRunner()
        cmd = self._make_command(include_quiet=True)
        result = runner.invoke(cmd, ["--quiet"])
        assert result.exit_code == 0

    def test_no_color_flag_accepted(self):
        runner = CliRunner()
        cmd = self._make_command(include_no_color=True)
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

    def test_verbose_not_passed_without_include(self):
        runner = CliRunner()
        received = {}

        @click.command()
        @common_cli_options(include_verbose=False)
        def cmd(**kwargs):
            received["kwargs"] = kwargs
            return []

        runner.invoke(cmd, ["--verbose"])
        assert "verbose" not in received.get("kwargs", {})

    def test_invalid_output_choice_fails(self):
        runner = CliRunner()
        cmd = self._make_command()
        result = runner.invoke(cmd, ["--output", "invalid_format"])
        assert result.exit_code != 0

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
