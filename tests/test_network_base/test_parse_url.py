"""Tests for nadzoring.network_base.parse_url."""

from nadzoring.network_base.parse_url import parse_url


class TestParseUrlReturnStructure:
    """Return value always contains all expected keys."""

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

    def test_full_url_has_all_keys(self):
        result = parse_url("https://user:pass@example.com:8080/path?k=v#frag")
        assert set(result.keys()) == self.REQUIRED_KEYS

    def test_minimal_url_has_all_keys(self):
        result = parse_url("http://example.com")
        assert set(result.keys()) == self.REQUIRED_KEYS

    def test_empty_string_has_all_keys(self):
        result = parse_url("")
        assert set(result.keys()) == self.REQUIRED_KEYS


class TestParseUrlFullUrl:
    """Full URL with all components."""

    def setup_method(self):
        self.url = "https://user:pass@example.com:8080/path/to/resource?foo=bar&baz=qux#section"
        self.result = parse_url(self.url)

    def test_original_preserved(self):
        assert self.result["original"] == self.url

    def test_protocol(self):
        assert self.result["protocol"] == "https"

    def test_username(self):
        assert self.result["username"] == "user"

    def test_password(self):
        assert self.result["password"] == "pass"

    def test_hostname(self):
        assert self.result["hostname"] == "example.com"

    def test_port(self):
        assert self.result["port"] == 8080

    def test_path(self):
        assert self.result["path"] == "/path/to/resource"

    def test_query_raw(self):
        assert self.result["query"] == "foo=bar&baz=qux"

    def test_query_params_parsed(self):
        assert ("foo", "bar") in self.result["query_params"]
        assert ("baz", "qux") in self.result["query_params"]

    def test_fragment(self):
        assert self.result["fragment"] == "section"


class TestParseUrlMinimalUrl:
    """URL with only scheme and host."""

    def setup_method(self):
        self.result = parse_url("http://example.com")

    def test_protocol(self):
        assert self.result["protocol"] == "http"

    def test_hostname(self):
        assert self.result["hostname"] == "example.com"

    def test_port_is_none(self):
        assert self.result["port"] is None

    def test_username_is_none(self):
        assert self.result["username"] is None

    def test_password_is_none(self):
        assert self.result["password"] is None

    def test_query_is_none(self):
        assert self.result["query"] is None

    def test_query_params_empty_list(self):
        assert self.result["query_params"] == []

    def test_fragment_is_none(self):
        assert self.result["fragment"] is None


class TestParseUrlEdgeCases:
    def test_empty_string_returns_nones(self):
        result = parse_url("")
        assert result["protocol"] is None
        assert result["hostname"] is None
        assert result["query_params"] == []

    def test_original_is_always_preserved(self):
        url = "totally invalid !! string"
        assert parse_url(url)["original"] == url

    def test_url_without_path(self):
        result = parse_url("ftp://files.example.com")
        assert result["protocol"] == "ftp"
        assert result["hostname"] == "files.example.com"

    def test_url_with_ip_address_host(self):
        result = parse_url("http://192.168.1.1:8080/api")
        assert result["hostname"] == "192.168.1.1"
        assert result["port"] == 8080
        assert result["path"] == "/api"

    def test_url_multiple_query_params(self):
        result = parse_url("https://example.com?a=1&b=2&c=3")
        params = dict(result["query_params"])
        assert params == {"a": "1", "b": "2", "c": "3"}

    def test_url_with_only_fragment(self):
        result = parse_url("http://example.com#top")
        assert result["fragment"] == "top"
        assert result["query"] is None

    def test_url_with_empty_query_string(self):
        result = parse_url("http://example.com?")
        assert result["query"] is None
        assert result["query_params"] == []

    def test_url_with_default_http_port(self):
        # urllib does not expose port when it matches the scheme default
        result = parse_url("http://example.com:80/")
        assert result["port"] == 80

    def test_url_with_auth_no_password(self):
        result = parse_url("http://user@example.com")
        assert result["username"] == "user"
        assert result["password"] is None

    def test_url_encoded_query(self):
        result = parse_url("https://example.com?q=hello+world&lang=en")
        assert result["query_params"][0][0] == "q"

    def test_path_root_slash(self):
        result = parse_url("https://example.com/")
        assert result["path"] == "/"

    def test_no_scheme_urlparse_behavior(self):
        # Without a scheme, urlparse treats the whole thing as path
        result = parse_url("example.com/path")
        # hostname will be None because no scheme was given
        assert result["hostname"] is None

    def test_query_params_type_is_list(self):
        result = parse_url("http://example.com?x=1")
        assert isinstance(result["query_params"], list)

    def test_port_type_is_int_or_none(self):
        result = parse_url("http://example.com:9000/")
        assert isinstance(result["port"], int)

    def test_repeated_query_key(self):
        result = parse_url("http://example.com?a=1&a=2")
        keys = [k for k, _ in result["query_params"]]
        assert keys.count("a") == 2
