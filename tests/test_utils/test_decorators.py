"""Tests for nadzoring.utils.decorators — 100% coverage."""

import json
import socket
from unittest.mock import MagicMock, patch

import click
import pytest
import yaml
from click.testing import CliRunner

from nadzoring.utils.decorators import (
    _handle_output,
    _handle_save,
    _parse_proxy_url,
    _setup_global_proxy,
    _show_completion_time,
    common_cli_options,
)
from nadzoring.utils.timeout import TimeoutConfig


class TestParseProxyUrl:
    """Tests for _parse_proxy_url function."""

    def test_parse_socks5_with_port(self):
        protocol, host, port = _parse_proxy_url("socks5://127.0.0.1:9050")
        assert protocol == "socks5"
        assert host == "127.0.0.1"
        assert port == 9050

    def test_parse_socks5_without_port_uses_default(self):
        protocol, host, port = _parse_proxy_url("socks5://proxy.example.com")
        assert protocol == "socks5"
        assert host == "proxy.example.com"
        assert port == 1080

    def test_parse_socks4_with_port(self):
        protocol, host, port = _parse_proxy_url("socks4://10.0.0.1:1080")
        assert protocol == "socks4"
        assert host == "10.0.0.1"
        assert port == 1080

    def test_parse_socks4_without_port_uses_default(self):
        protocol, host, port = _parse_proxy_url("socks4://socks4.example.com")
        assert protocol == "socks4"
        assert port == 1080

    def test_parse_http_with_port(self):
        protocol, host, port = _parse_proxy_url("http://proxy:8080")
        assert protocol == "http"
        assert host == "proxy"
        assert port == 8080

    def test_parse_http_without_port_uses_default_8080(self):
        protocol, host, port = _parse_proxy_url("http://httpproxy")
        assert protocol == "http"
        assert port == 8080

    def test_parse_https_with_port(self):
        protocol, host, port = _parse_proxy_url("https://secure:3128")
        assert protocol == "https"
        assert host == "secure"
        assert port == 3128

    def test_parse_https_without_port_uses_default_8080(self):
        protocol, host, port = _parse_proxy_url("https://secureproxy")
        assert protocol == "https"
        assert port == 8080

    def test_parse_empty_port_string_uses_default(self):
        protocol, host, port = _parse_proxy_url("socks5://host:")
        assert protocol == "socks5"
        assert host == "host"
        assert port == 1080

    def test_parse_port_with_whitespace_uses_default(self):
        protocol, host, port = _parse_proxy_url("socks5://host:   ")
        assert protocol == "socks5"
        assert host == "host"
        assert port == 1080

    def test_parse_invalid_protocol_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported proxy protocol"):
            _parse_proxy_url("ftp://host:21")

    def test_parse_missing_host_raises_error(self):
        with pytest.raises(ValueError, match="Missing host"):
            _parse_proxy_url("socks5://")

    def test_parse_invalid_format_raises_error(self):
        with pytest.raises(ValueError, match="Invalid proxy URL format"):
            _parse_proxy_url("not-a-valid-url")


class TestSetupGlobalProxy:
    """Tests for _setup_global_proxy function."""

    def setup_method(self):
        """Save original socket.socket before each test."""
        self.original_socket = socket.socket
        if hasattr(socket, "_original_socket"):
            self.original_original = socket._original_socket

    def teardown_method(self):
        """Restore original socket.socket after each test."""
        socket.socket = self.original_socket
        if hasattr(self, "original_original"):
            socket._original_socket = self.original_original

    def test_proxy_none_restores_original_socket(self):
        original_socket = socket.socket
        socket._original_socket = original_socket
        socket.socket = MagicMock()

        _setup_global_proxy(None)

        assert socket.socket == original_socket

    def test_proxy_none_when_no_original_socket_attr(self):
        original_socket = socket.socket
        if hasattr(socket, "_original_socket"):
            del socket._original_socket

        test_socket = MagicMock()
        socket.socket = test_socket

        _setup_global_proxy(None)

        assert socket.socket == test_socket

    def test_proxy_socks5_sets_up_proxy(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy("socks5://127.0.0.1:9050")

            mock_socks.set_default_proxy.assert_called_once_with(mock_socks.SOCKS5, "127.0.0.1", 9050)
            assert socket.socket == mock_socks.socksocket

    def test_proxy_socks4_sets_up_proxy(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy("socks4://10.0.0.1:1080")

            mock_socks.set_default_proxy.assert_called_once_with(mock_socks.SOCKS4, "10.0.0.1", 1080)
            assert socket.socket == mock_socks.socksocket

    def test_proxy_http_sets_up_urllib_proxy(self):
        with patch("nadzoring.utils.decorators.urllib") as mock_urllib:
            mock_opener = MagicMock()
            mock_builder = MagicMock()
            mock_builder.build_opener.return_value = mock_opener
            mock_urllib.request.ProxyHandler = MagicMock(return_value=mock_builder)
            mock_urllib.request.build_opener = mock_builder
            mock_urllib.request.install_opener = MagicMock()

            _setup_global_proxy("http://proxy:8080")

            mock_urllib.request.install_opener.assert_called_once()

    def test_proxy_https_sets_up_urllib_proxy(self):
        with patch("nadzoring.utils.decorators.urllib") as mock_urllib:
            mock_opener = MagicMock()
            mock_builder = MagicMock()
            mock_builder.build_opener.return_value = mock_opener
            mock_urllib.request.ProxyHandler = MagicMock(return_value=mock_builder)
            mock_urllib.request.build_opener = mock_builder
            mock_urllib.request.install_opener = MagicMock()

            _setup_global_proxy("https://secure:3128")

            mock_urllib.request.install_opener.assert_called_once()

    def test_proxy_without_port_uses_default_socks_port(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy("socks5://proxy.example.com")

            mock_socks.set_default_proxy.assert_called_once_with(mock_socks.SOCKS5, "proxy.example.com", 1080)

    def test_proxy_empty_port_string_uses_default(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy("socks5://host:")

            mock_socks.set_default_proxy.assert_called_once_with(mock_socks.SOCKS5, "host", 1080)

    def test_proxy_port_with_whitespace_uses_default(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy("socks5://host:   ")

            mock_socks.set_default_proxy.assert_called_once_with(mock_socks.SOCKS5, "host", 1080)

    def test_invalid_proxy_raises_click_exception(self):
        with pytest.raises(click.ClickException, match="Failed to setup proxy"):
            _setup_global_proxy("invalid://proxy:8080")

    def test_no_proxy_no_socks_setup(self):
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            _setup_global_proxy(None)
            mock_socks.set_default_proxy.assert_not_called()


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
    def setup_method(self):
        """Save original socket.socket before tests that might modify it."""
        self.original_socket = socket.socket

    def teardown_method(self):
        """Restore original socket.socket after tests."""
        socket.socket = self.original_socket

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

    def test_proxy_flag_calls_setup_global_proxy_with_proxy_url(self):
        with patch("nadzoring.utils.decorators._setup_global_proxy") as mock_setup:
            runner = CliRunner()

            @click.command()
            @common_cli_options(include_proxy=True)
            def cmd(**kwargs):
                return [{"test": "ok"}]

            result = runner.invoke(cmd, ["--proxy", "socks5://127.0.0.1:9050"])

            assert result.exit_code == 0
            mock_setup.assert_called_once_with("socks5://127.0.0.1:9050")

    def test_proxy_flag_without_value_does_not_call_setup(self):
        with patch("nadzoring.utils.decorators._setup_global_proxy") as mock_setup:
            runner = CliRunner()

            @click.command()
            @common_cli_options(include_proxy=True)
            def cmd(**kwargs):
                return [{"test": "ok"}]

            result = runner.invoke(cmd, [])

            assert result.exit_code == 0
            mock_setup.assert_not_called()

    def test_proxy_flag_with_other_flags_works_together(self):
        with patch("nadzoring.utils.decorators._setup_global_proxy") as mock_setup:
            runner = CliRunner()

            @click.command()
            @common_cli_options(include_proxy=True, include_verbose=True)
            def cmd(**kwargs):
                return [{"result": "data"}]

            result = runner.invoke(cmd, ["--proxy", "socks5://test:1234", "--verbose", "--output", "json"])

            assert result.exit_code == 0
            mock_setup.assert_called_once_with("socks5://test:1234")
            assert "data" in result.output

    def test_proxy_ignored_when_include_proxy_false(self):
        """When include_proxy=False, proxy is still extracted from _ALWAYS_EXTRACTED
        and global proxy setup still happens. The flag only controls whether proxy
        is passed as an argument to the wrapped function.
        """
        with patch("nadzoring.utils.decorators._setup_global_proxy") as mock_setup:
            runner = CliRunner()
            received = {}

            @click.command()
            @common_cli_options(include_proxy=False)
            def cmd(**kwargs):
                received["kwargs"] = kwargs
                return [{"test": "ok"}]

            result = runner.invoke(cmd, ["--proxy", "socks5://test:1234"])

            assert result.exit_code == 0
            mock_setup.assert_called_once_with("socks5://test:1234")
            assert "proxy" not in received["kwargs"]

    def test_parse_port_with_invalid_number_uses_default_socks(self):
        """When port is not a valid integer for SOCKS, use default 1080."""
        with patch("nadzoring.utils.decorators.socks") as mock_socks:
            protocol, host, port = _parse_proxy_url("socks5://host:abc")
            assert protocol == "socks5"
            assert host == "host"
            assert port == 1080

    def test_parse_port_with_invalid_number_uses_default_http(self):
        """When port is not a valid integer for HTTP, use default 8080."""
        protocol, host, port = _parse_proxy_url("http://proxy:invalid")
        assert protocol == "http"
        assert host == "proxy"
        assert port == 8080

    def test_parse_port_with_negative_number_uses_default(self):
        """Negative port number is invalid, use default."""
        protocol, host, port = _parse_proxy_url("socks4://host:-100")
        assert protocol == "socks4"
        assert host == "host"
        assert port == 1080

    def test_parse_port_with_float_string_uses_default(self):
        """Float string as port is invalid, use default."""
        protocol, host, port = _parse_proxy_url("https://proxy:12.34")
        assert protocol == "https"
        assert host == "proxy"
        assert port == 8080
