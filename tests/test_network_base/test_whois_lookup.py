"""Tests for nadzoring.network_base.whois_lookup — 100% coverage."""

import math

from nadzoring.network_base.whois_lookup import (
    _WHOIS_FIELD_MAP,
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


def test_is_ip_valid_ipv4():
    assert _is_ip("1.2.3.4") is True


def test_is_ip_valid_ipv6():
    assert _is_ip("2001:db8::1") is True


def test_is_ip_loopback():
    assert _is_ip("127.0.0.1") is True


def test_is_ip_broadcast():
    assert _is_ip("255.255.255.255") is True


def test_is_ip_domain_false():
    assert _is_ip("example.com") is False


def test_is_ip_empty_string_false():
    assert _is_ip("") is False


def test_is_ip_partial_ip_false():
    assert _is_ip("192.168.1") is False


def test_is_ip_returns_bool():
    assert isinstance(_is_ip("1.1.1.1"), bool)


# ---------------------------------------------------------------------------
# _run_whois_command
# ---------------------------------------------------------------------------


def test_run_whois_linux_returns_string(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    mocker.patch(
        "nadzoring.network_base.whois_lookup.check_output",
        return_value=b"Domain Name: EXAMPLE.COM\n",
    )
    result = _run_whois_command("example.com")
    assert isinstance(result, str)
    assert "EXAMPLE.COM" in result


def test_run_whois_windows_uses_cp866(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup.system", return_value="Windows")
    mocker.patch(
        "nadzoring.network_base.whois_lookup.check_output",
        return_value="data".encode("cp866"),
    )
    result = _run_whois_command("1.2.3.4")
    assert result is not None


def test_run_whois_file_not_found_returns_none(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    mocker.patch(
        "nadzoring.network_base.whois_lookup.check_output",
        side_effect=FileNotFoundError,
    )
    assert _run_whois_command("example.com") is None


def test_run_whois_timeout_returns_none(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    mocker.patch(
        "nadzoring.network_base.whois_lookup.check_output",
        side_effect=TimeoutError,
    )
    assert _run_whois_command("example.com") is None


def test_run_whois_called_process_error_returns_none(mocker):
    from subprocess import CalledProcessError

    mocker.patch("nadzoring.network_base.whois_lookup.system", return_value="Linux")
    mocker.patch(
        "nadzoring.network_base.whois_lookup.check_output",
        side_effect=CalledProcessError(1, "whois"),
    )
    assert _run_whois_command("example.com") is None


# ---------------------------------------------------------------------------
# _parse_whois_output
# ---------------------------------------------------------------------------

SAMPLE_WHOIS = (
    "% comment\n"
    "# hash comment\n"
    "Registrar: ACME Registrar\n"
    "Creation Date: 2000-01-01T00:00:00Z\n"
    "Registry Expiry Date: 2030-01-01T00:00:00Z\n"
    "Updated Date: 2023-06-15T00:00:00Z\n"
    "Name Server: ns1.example.com\n"
    "Name Server: ns2.example.com\n"
    "Domain Status: clientDeleteProhibited\n"
    "Registrant Country: US\n"
    "Registrant Organization: Example Org\n"
    "Abuse Contact Email: abuse@example.com\n"
    "NetRange: 192.0.2.0 - 192.0.2.255\n"
    "OrgName: Example Org\n"
    "CIDR: 192.0.2.0/24\n"
    "OriginAS: AS12345\n"
)


def test_parse_registrar():
    assert _parse_whois_output(SAMPLE_WHOIS)["registrar"] == "ACME Registrar"


def test_parse_creation_date():
    assert _parse_whois_output(SAMPLE_WHOIS)["creation_date"] == "2000-01-01T00:00:00Z"


def test_parse_expiry_date():
    assert _parse_whois_output(SAMPLE_WHOIS)["expiry_date"] == "2030-01-01T00:00:00Z"


def test_parse_updated_date():
    assert _parse_whois_output(SAMPLE_WHOIS)["updated_date"] == "2023-06-15T00:00:00Z"


def test_parse_name_servers_first_only():
    assert _parse_whois_output(SAMPLE_WHOIS)["name_servers"] == "ns1.example.com"


def test_parse_status():
    assert _parse_whois_output(SAMPLE_WHOIS)["status"] == "clientDeleteProhibited"


def test_parse_country():
    assert _parse_whois_output(SAMPLE_WHOIS)["country"] == "US"


def test_parse_registrant_org():
    assert _parse_whois_output(SAMPLE_WHOIS)["registrant_org"] == "Example Org"


def test_parse_abuse_email():
    assert _parse_whois_output(SAMPLE_WHOIS)["abuse_email"] == "abuse@example.com"


def test_parse_netrange():
    assert _parse_whois_output(SAMPLE_WHOIS)["netrange"] == "192.0.2.0 - 192.0.2.255"


def test_parse_org_name():
    assert _parse_whois_output(SAMPLE_WHOIS)["org_name"] == "Example Org"


def test_parse_cidr():
    assert _parse_whois_output(SAMPLE_WHOIS)["cidr"] == "192.0.2.0/24"


def test_parse_asn():
    assert _parse_whois_output(SAMPLE_WHOIS)["asn"] == "AS12345"


def test_parse_percent_comment_ignored():
    result = _parse_whois_output("% this is a comment\nRegistrar: Test\n")
    assert result["registrar"] == "Test"


def test_parse_hash_comment_ignored():
    result = _parse_whois_output("# hash comment\nRegistrar: Test2\n")
    assert result["registrar"] == "Test2"


def test_parse_empty_input_all_none():
    result = _parse_whois_output("")
    for key in [
        "registrar",
        "creation_date",
        "expiry_date",
        "updated_date",
        "name_servers",
        "status",
        "registrant_org",
        "country",
        "abuse_email",
        "netrange",
        "org_name",
        "cidr",
        "asn",
    ]:
        assert result[key] is None


def test_parse_missing_field_is_none():
    result = _parse_whois_output("Registrar: ACME\n")
    assert result["asn"] is None


def test_parse_unknown_key_not_in_result():
    result = _parse_whois_output("Unknown-Key: value\n")
    assert "Unknown-Key" not in result


def test_parse_empty_value_not_captured():
    result = _parse_whois_output("Registrar:\n")
    assert result["registrar"] is None


def test_parse_case_insensitive_prefix():
    result = _parse_whois_output("REGISTRAR: CaseTest\n")
    assert result["registrar"] == "CaseTest"


def test_parse_blank_lines_skipped():
    result = _parse_whois_output("\n\nRegistrar: Blanklines\n\n")
    assert result["registrar"] == "Blanklines"


def test_parse_no_fields_extracted_all_none():
    raw = "Some random output\nwith no known fields\n"
    result = _parse_whois_output(raw)
    for key in [
        "registrar",
        "creation_date",
        "expiry_date",
        "updated_date",
        "name_servers",
        "status",
        "registrant_org",
        "country",
        "abuse_email",
        "netrange",
        "org_name",
        "cidr",
        "asn",
    ]:
        assert result[key] is None


# ---------------------------------------------------------------------------
# _format_whois_value
# ---------------------------------------------------------------------------


def test_format_none_returns_empty_string():
    assert _format_whois_value(None) == ""


def test_format_str_returns_as_is():
    assert _format_whois_value("hello") == "hello"


def test_format_list_joined_by_newline():
    assert _format_whois_value(["a", "b", "c"]) == "a\nb\nc"


def test_format_nested_list():
    result = _format_whois_value(["x", "y"])
    assert "x" in result and "y" in result


def test_format_datetime_like_uses_isoformat(mocker):
    mock_dt = mocker.MagicMock()
    mock_dt.isoformat.return_value = "2023-01-01T00:00:00"
    assert _format_whois_value(mock_dt) == "2023-01-01T00:00:00"


def test_format_int_stringified():
    assert _format_whois_value(42) == "42"


def test_format_float_stringified():
    assert _format_whois_value(math.pi)[:4] == "3.14"


# ---------------------------------------------------------------------------
# whois_lookup
# ---------------------------------------------------------------------------


def test_whois_lookup_success_returns_dict(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Registrar: ACME\nRegistrant Country: US\n",
    )
    result = whois_lookup("example.com")
    assert isinstance(result, dict)
    assert result["registrar"] == "ACME"


def test_whois_lookup_target_in_result(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Registrar: X\n",
    )
    result = whois_lookup("example.com")
    assert result["target"] == "example.com"


def test_whois_lookup_domain_type(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Registrar: X\n",
    )
    result = whois_lookup("example.com")
    assert result["type"] == "domain"


def test_whois_lookup_ip_type(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="OrgName: ACME\n",
    )
    result = whois_lookup("8.8.8.8")
    assert result["type"] == "ip"


def test_whois_lookup_command_none_returns_error_dict(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    result = whois_lookup("example.com")
    assert "error" in result


def test_whois_lookup_error_includes_target(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    result = whois_lookup("example.com")
    assert result["target"] == "example.com"


def test_whois_lookup_error_includes_type_domain(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    result = whois_lookup("example.com")
    assert result["type"] == "domain"


def test_whois_lookup_error_includes_type_ip(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    result = whois_lookup("1.2.3.4")
    assert result["type"] == "ip"


def test_whois_lookup_error_message_mentions_whois(mocker):
    mocker.patch("nadzoring.network_base.whois_lookup._run_whois_command", return_value=None)
    result = whois_lookup("example.com")
    assert "command not found" in result["error"].lower()


def test_whois_lookup_no_fields_parsed_adds_error(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Random output without any known fields\n",
    )
    result = whois_lookup("example.com")
    assert result.get("error") == "No information found"


# ---------------------------------------------------------------------------
# whois_domain_lookup
# ---------------------------------------------------------------------------


def test_whois_domain_lookup_returns_list(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup.whois.whois",
        return_value={"registrar": "ACME", "creation_date": "2000-01-01"},
    )
    result = whois_domain_lookup("example.com")
    assert isinstance(result, list)


def test_whois_domain_lookup_items_are_dicts(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup.whois.whois",
        return_value={"registrar": "ACME"},
    )
    result = whois_domain_lookup("example.com")
    assert all(isinstance(item, dict) for item in result)


def test_whois_domain_lookup_field_value_keys(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup.whois.whois",
        return_value={"registrar": "ACME"},
    )
    result = whois_domain_lookup("example.com")
    for item in result:
        assert "Field" in item or "error" in item


def test_whois_domain_lookup_exception_returns_error_list(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup.whois.whois",
        side_effect=Exception("lookup failed"),
    )
    result = whois_domain_lookup("bad.domain")
    assert len(result) == 1
    assert "error" in result[0]


def test_whois_domain_lookup_exception_error_mentions_domain(mocker):
    mocker.patch(
        "nadzoring.network_base.whois_lookup.whois.whois",
        side_effect=Exception("lookup failed"),
    )
    result = whois_domain_lookup("bad.domain")
    assert "bad.domain" in result[0]["error"]


# Add these tests to test_whois_lookup.py after the existing whois_lookup tests

# ---------------------------------------------------------------------------
# Additional whois_lookup tests for 100% coverage
# ---------------------------------------------------------------------------


def test_whois_lookup_unexpected_exception(mocker):
    """Test that unexpected exceptions are caught and handled (line 150)."""
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        side_effect=RuntimeError("Something unexpected happened"),
    )
    result = whois_lookup("example.com")
    assert "error" in result
    assert "Unexpected error" in result["error"]
    assert result["target"] == "example.com"
    assert result["type"] == "domain"


def test_whois_lookup_no_fields_found_adds_error(mocker):
    """Test that when no WHOIS fields are parsed, error is added (lines 169-176)."""
    # This returns raw output that doesn't match any field patterns
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Some arbitrary text\nthat doesn't match any\nof the WHOIS field patterns\n",
    )
    result = whois_lookup("example.com")
    # All fields should be None, so error should be set
    assert result["error"] == "No information found"
    assert result["target"] == "example.com"
    assert result["type"] == "domain"
    # Verify all fields are None
    for key in _WHOIS_FIELD_MAP:
        assert result.get(key) is None


def test_whois_lookup_partial_fields_no_error(mocker):
    """Test that when at least one field is found, no error is added (lines 169-176)."""
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Registrar: Test Registrar\nSome other text\n",
    )
    result = whois_lookup("example.com")
    # At least one field was found, so error should be None
    assert result["error"] is None
    assert result["registrar"] == "Test Registrar"
    assert result["target"] == "example.com"


def test_whois_lookup_empty_raw_output(mocker):
    """Test that empty raw output triggers 'No information found' error."""
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="",
    )
    result = whois_lookup("example.com")
    assert result["error"] == "No information found"
    # All fields should be None
    for key in _WHOIS_FIELD_MAP:
        assert result.get(key) is None


def test_whois_lookup_invalid_target_dash_prefix(mocker):
    """Test invalid target starting with dash (already covered but for completeness)."""
    result = whois_lookup("-example.com")
    assert result["error"] == "Invalid target"
    assert result["type"] == "unknown"
    assert result["target"] == "-example.com"


def test_whois_lookup_none_target(mocker):
    """Test None target (already covered but for completeness)."""
    result = whois_lookup("")
    assert result["error"] == "Invalid target"
    assert result["type"] == "unknown"
    assert result["target"] == ""


def test_whois_lookup_command_failure_specific_error(mocker):
    """Test that command failure returns the specific error message."""
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value=None,
    )
    result = whois_lookup("example.com")
    assert result["error"] == "Command not found or query failed"
    assert result["target"] == "example.com"
    assert result["type"] == "domain"


def test_whois_lookup_ip_address_no_fields(mocker):
    """Test IP lookup that returns no matching fields."""
    mocker.patch(
        "nadzoring.network_base.whois_lookup._run_whois_command",
        return_value="Some random IP WHOIS output\nwith no matching fields\n",
    )
    result = whois_lookup("8.8.8.8")
    assert result["error"] == "No information found"
    assert result["type"] == "ip"
    assert result["target"] == "8.8.8.8"
