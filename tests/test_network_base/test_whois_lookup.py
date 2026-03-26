"""Tests for nadzoring.network_base.whois_lookup."""

from unittest.mock import MagicMock, patch

from nadzoring.network_base.whois_lookup import (
    _format_whois_value,
    _is_ip,
    _parse_whois_output,
    _run_whois_command,
    whois_domain_lookup,
    whois_lookup,
)

# ---------------------------------------------------------------------------
# _is_ip
# ---------------------------------------------------------------------------


class TestIsIp:
    def test_valid_ipv4_true(self):
        assert _is_ip("1.2.3.4") is True

    def test_valid_ipv6_true(self):
        assert _is_ip("2001:db8::1") is True

    def test_domain_false(self):
        assert _is_ip("example.com") is False

    def test_empty_string_false(self):
        assert _is_ip("") is False

    def test_partial_ip_false(self):
        assert _is_ip("192.168.1") is False

    def test_loopback_true(self):
        assert _is_ip("127.0.0.1") is True

    def test_broadcast_true(self):
        assert _is_ip("255.255.255.255") is True


# ---------------------------------------------------------------------------
# _run_whois_command
# ---------------------------------------------------------------------------


class TestRunWhoisCommand:
    @patch("nadzoring.network_base.whois_lookup.check_output")
    @patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    def test_linux_returns_decoded_string(self, mock_sys, mock_co):
        mock_co.return_value = b"Domain Name: EXAMPLE.COM\n"
        result = _run_whois_command("example.com")
        assert "EXAMPLE.COM" in result
        assert isinstance(result, str)

    @patch("nadzoring.network_base.whois_lookup.check_output")
    @patch("nadzoring.network_base.whois_lookup.system", return_value="Windows")
    def test_windows_uses_cp866(self, mock_sys, mock_co):
        mock_co.return_value = "data".encode("cp866")
        result = _run_whois_command("1.2.3.4")
        assert result is not None

    @patch(
        "nadzoring.network_base.whois_lookup.check_output",
        side_effect=FileNotFoundError,
    )
    @patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    def test_file_not_found_returns_none(self, mock_sys, mock_co):
        assert _run_whois_command("example.com") is None

    @patch(
        "nadzoring.network_base.whois_lookup.check_output",
        side_effect=TimeoutError,
    )
    @patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    def test_timeout_returns_none(self, mock_sys, mock_co):
        assert _run_whois_command("example.com") is None


# ---------------------------------------------------------------------------
# _parse_whois_output
# ---------------------------------------------------------------------------


class TestParseWhoisOutput:
    SAMPLE_RAW = (
        "% This is a comment\n"
        "Registrar: ACME Registrar Inc.\n"
        "Creation Date: 2000-01-01T00:00:00Z\n"
        "Registry Expiry Date: 2030-01-01T00:00:00Z\n"
        "Updated Date: 2023-06-15T00:00:00Z\n"
        "Name Server: ns1.example.com\n"
        "Name Server: ns2.example.com\n"
        "Domain Status: clientDeleteProhibited\n"
        "Registrant Country: US\n"
    )

    def test_registrar_extracted(self):
        result = _parse_whois_output(self.SAMPLE_RAW)
        assert result["registrar"] == "ACME Registrar Inc."

    def test_creation_date_extracted(self):
        result = _parse_whois_output(self.SAMPLE_RAW)
        assert result["creation_date"] == "2000-01-01T00:00:00Z"

    def test_expiry_date_extracted(self):
        result = _parse_whois_output(self.SAMPLE_RAW)
        assert result["expiry_date"] == "2030-01-01T00:00:00Z"

    def test_country_extracted(self):
        result = _parse_whois_output(self.SAMPLE_RAW)
        assert result["country"] == "US"

    def test_name_server_first_occurrence_only(self):
        result = _parse_whois_output(self.SAMPLE_RAW)
        # Only first occurrence captured
        assert result["name_servers"] == "ns1.example.com"

    def test_comment_lines_ignored(self):
        result = _parse_whois_output("% comment line\nRegistrar: Test\n")
        assert result["registrar"] == "Test"

    def test_hash_comment_lines_ignored(self):
        result = _parse_whois_output("# another comment\nRegistrar: Test2\n")
        assert result["registrar"] == "Test2"

    def test_empty_input_all_none(self):
        result = _parse_whois_output("")
        assert all(v is None for v in result.values())

    def test_unknown_field_not_in_result(self):
        result = _parse_whois_output("SomeUnknownKey: value\n")
        assert "SomeUnknownKey" not in result

    def test_missing_fields_are_none(self):
        result = _parse_whois_output("Registrar: ACME\n")
        assert result["asn"] is None


# ---------------------------------------------------------------------------
# _format_whois_value
# ---------------------------------------------------------------------------


class TestFormatWhoisValue:
    def test_none_returns_empty_string(self):
        assert _format_whois_value(None) == ""

    def test_str_value_returned_as_is(self):
        assert _format_whois_value("example") == "example"

    def test_list_joined_with_newline(self):
        result = _format_whois_value(["a", "b", "c"])
        assert result == "a\nb\nc"

    def test_nested_list(self):
        result = _format_whois_value([["x"], "y"])
        assert "x" in result
        assert "y" in result

    def test_datetime_like_isoformat_used(self):
        mock_dt = MagicMock()
        mock_dt.isoformat.return_value = "2023-01-01T00:00:00"
        result = _format_whois_value(mock_dt)
        assert result == "2023-01-01T00:00:00"

    def test_int_value_stringified(self):
        assert _format_whois_value(42) == "42"


# ---------------------------------------------------------------------------
# whois_lookup
# ---------------------------------------------------------------------------


class TestWhoisLookup:
    @patch("nadzoring.network_base.whois_lookup._run_whois_command")
    def test_successful_lookup_returns_dict(self, mock_run):
        mock_run.return_value = "Registrar: ACME\nRegistrant Country: US\n"
        result = whois_lookup("example.com")
        assert isinstance(result, dict)
        assert result["registrar"] == "ACME"

    @patch("nadzoring.network_base.whois_lookup._run_whois_command")
    def test_target_and_type_always_present(self, mock_run):
        mock_run.return_value = "Registrar: X\n"
        result = whois_lookup("example.com")
        assert result["target"] == "example.com"
        assert result["type"] == "domain"

    @patch("nadzoring.network_base.whois_lookup._run_whois_command")
    def test_ip_target_type_is_ip(self, mock_run):
        mock_run.return_value = "OrgName: Example Org\n"
        result = whois_lookup("8.8.8.8")
        assert result["type"] == "ip"

    @patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    def test_command_failure_returns_error_dict(self, mock_run):
        result = whois_lookup("example.com")
        assert "error" in result
        assert result["target"] == "example.com"

    @patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    def test_error_dict_includes_install_hint(self, mock_run):
        result = whois_lookup("example.com")
        assert "whois" in result["error"].lower()


# ---------------------------------------------------------------------------
# whois_domain_lookup
# ---------------------------------------------------------------------------


class TestWhoisDomainLookup:
    @patch("nadzoring.network_base.whois_lookup.whois")
    def test_returns_list_of_dicts(self, mock_whois_module):
        mock_info = {"registrar": "ACME", "creation_date": "2000-01-01"}
        mock_whois_module.whois.return_value = mock_info
        result = whois_domain_lookup("example.com")
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    @patch("nadzoring.network_base.whois_lookup.whois")
    def test_each_item_has_field_and_value_keys(self, mock_whois_module):
        mock_whois_module.whois.return_value = {"registrar": "ACME"}
        result = whois_domain_lookup("example.com")
        for item in result:
            assert "Field" in item or "error" in item

    @patch("nadzoring.network_base.whois_lookup.whois")
    def test_exception_returns_error_list(self, mock_whois_module):
        mock_whois_module.whois.side_effect = Exception("lookup failed")
        result = whois_domain_lookup("bad.domain")
        assert len(result) == 1
        assert "error" in result[0]
