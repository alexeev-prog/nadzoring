"""Tests for nadzoring.network_base.parse_url — 100% coverage."""

import pytest

from nadzoring.network_base.parse_url import parse_url

REQUIRED_KEYS = {
    "original",
    "protocol",
    "username",
    "password",
    "hostname",
    "port",
    "path",
    "query",
    "query_params",
    "fragment",
}


# ---------------------------------------------------------------------------
# Return structure
# ---------------------------------------------------------------------------


def test_full_url_has_all_keys():
    assert set(parse_url("https://user:pass@example.com:8080/path?k=v#f").keys()) == REQUIRED_KEYS


def test_minimal_url_has_all_keys():
    assert set(parse_url("http://example.com").keys()) == REQUIRED_KEYS


def test_empty_string_has_all_keys():
    assert set(parse_url("").keys()) == REQUIRED_KEYS


# ---------------------------------------------------------------------------
# Full URL
# ---------------------------------------------------------------------------


@pytest.fixture
def full_result():
    return parse_url("https://user:pass@example.com:8080/path/to?foo=bar&baz=qux#section")


def test_original_preserved(full_result):
    assert full_result["original"] == "https://user:pass@example.com:8080/path/to?foo=bar&baz=qux#section"


def test_protocol(full_result):
    assert full_result["protocol"] == "https"


def test_username(full_result):
    assert full_result["username"] == "user"


def test_password(full_result):
    assert full_result["password"] == "pass"


def test_hostname(full_result):
    assert full_result["hostname"] == "example.com"


def test_port(full_result):
    assert full_result["port"] == 8080


def test_path(full_result):
    assert full_result["path"] == "/path/to"


def test_query_raw(full_result):
    assert full_result["query"] == "foo=bar&baz=qux"


def test_query_params_contains_foo(full_result):
    assert ("foo", "bar") in full_result["query_params"]


def test_query_params_contains_baz(full_result):
    assert ("baz", "qux") in full_result["query_params"]


def test_fragment(full_result):
    assert full_result["fragment"] == "section"


# ---------------------------------------------------------------------------
# Minimal URL — all optional fields are None / empty
# ---------------------------------------------------------------------------


@pytest.fixture
def minimal_result():
    return parse_url("http://example.com")


def test_minimal_protocol(minimal_result):
    assert minimal_result["protocol"] == "http"


def test_minimal_hostname(minimal_result):
    assert minimal_result["hostname"] == "example.com"


def test_minimal_port_none(minimal_result):
    assert minimal_result["port"] is None


def test_minimal_username_none(minimal_result):
    assert minimal_result["username"] is None


def test_minimal_password_none(minimal_result):
    assert minimal_result["password"] is None


def test_minimal_query_none(minimal_result):
    assert minimal_result["query"] is None


def test_minimal_query_params_empty(minimal_result):
    assert minimal_result["query_params"] == []


def test_minimal_fragment_none(minimal_result):
    assert minimal_result["fragment"] is None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_string_protocol_none():
    assert parse_url("")["protocol"] is None


def test_empty_string_hostname_none():
    assert parse_url("")["hostname"] is None


def test_empty_string_query_params_empty():
    assert parse_url("")["query_params"] == []


def test_original_preserved_for_invalid():
    raw = "not a url at all"
    assert parse_url(raw)["original"] == raw


def test_ip_host():
    result = parse_url("http://192.168.1.1:9000/api")
    assert result["hostname"] == "192.168.1.1"
    assert result["port"] == 9000
    assert result["path"] == "/api"


def test_path_root_slash():
    assert parse_url("https://example.com/")["path"] == "/"


def test_query_empty_string_is_none():
    assert parse_url("http://example.com?")["query"] is None


def test_query_params_empty_on_no_query():
    assert parse_url("http://example.com?")["query_params"] == []


def test_fragment_only():
    result = parse_url("http://example.com#top")
    assert result["fragment"] == "top"
    assert result["query"] is None


def test_auth_no_password():
    result = parse_url("http://user@example.com")
    assert result["username"] == "user"
    assert result["password"] is None


def test_repeated_query_key():
    result = parse_url("http://example.com?a=1&a=2")
    keys = [k for k, _ in result["query_params"]]
    assert keys.count("a") == 2


def test_query_params_type_list():
    assert isinstance(parse_url("http://example.com?x=1")["query_params"], list)


def test_port_type_int():
    assert isinstance(parse_url("http://example.com:8080/")["port"], int)


def test_ftp_scheme():
    result = parse_url("ftp://files.example.com")
    assert result["protocol"] == "ftp"


def test_no_scheme_hostname_none():
    # Without scheme urlparse treats everything as path
    assert parse_url("example.com/path")["hostname"] is None


def test_path_none_when_missing():
    # "http://example.com" → path is "" → becomes None
    result = parse_url("http://example.com")
    assert result["path"] is None
