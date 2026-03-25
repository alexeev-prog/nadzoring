"""Tests for nadzoring.utils.validators."""

from nadzoring.utils.validators import (
    resolve_hostname,
    validate_domain,
    validate_ip,
    validate_ipv4,
    validate_ipv6,
    validate_port,
)


class TestValidateDomain:
    def test_valid_simple(self):
        assert validate_domain("example.com") is True

    def test_valid_subdomain(self):
        assert validate_domain("sub.example.com") is True

    def test_valid_deep_subdomain(self):
        assert validate_domain("a.b.c.example.com") is True

    def test_valid_trailing_dot(self):
        assert validate_domain("example.com.") is True

    def test_valid_single_label(self):
        assert validate_domain("localhost") is True

    def test_valid_numeric_labels(self):
        assert validate_domain("123.example.com") is True

    def test_valid_hyphen_in_middle(self):
        assert validate_domain("my-domain.example.com") is True

    def test_valid_mixed_case(self):
        assert validate_domain("Example.COM") is True

    def test_invalid_empty_string(self):
        assert validate_domain("") is False

    def test_invalid_too_long(self):
        assert validate_domain("a" * 256) is False

    def test_invalid_leading_hyphen(self):
        assert validate_domain("-bad.example.com") is False

    def test_invalid_trailing_hyphen(self):
        assert validate_domain("bad-.example.com") is False

    def test_invalid_label_too_long(self):
        assert validate_domain(f"{'a' * 64}.example.com") is False

    def test_invalid_underscore(self):
        assert validate_domain("_foo.example.com") is False

    def test_invalid_space(self):
        assert validate_domain("ex ample.com") is False

    def test_invalid_at_symbol(self):
        assert validate_domain("user@example.com") is False

    def test_exactly_255_chars(self):
        label = "a" * 63
        domain = f"{label}.{label}.{label}.{'a' * (255 - 3 * 64)}"
        assert len(domain) <= 255
        assert validate_domain(domain) is True

    def test_exactly_256_chars(self):
        assert validate_domain("a" * 256) is False


class TestValidateIp:
    def test_valid_ipv4(self):
        assert validate_ip("8.8.8.8") is True

    def test_valid_ipv6_loopback(self):
        assert validate_ip("::1") is True

    def test_valid_ipv6_full(self):
        assert validate_ip("2001:db8::1") is True

    def test_valid_ipv4_loopback(self):
        assert validate_ip("127.0.0.1") is True

    def test_invalid_string(self):
        assert validate_ip("not-an-ip") is False

    def test_invalid_empty(self):
        assert validate_ip("") is False

    def test_invalid_partial_ipv4(self):
        assert validate_ip("192.168.1") is False

    def test_invalid_out_of_range_octet(self):
        assert validate_ip("256.0.0.1") is False

    def test_invalid_domain_like(self):
        assert validate_ip("example.com") is False


class TestValidateIpv4:
    def test_valid_private(self):
        assert validate_ipv4("192.168.1.1") is True

    def test_valid_public(self):
        assert validate_ipv4("8.8.8.8") is True

    def test_valid_loopback(self):
        assert validate_ipv4("127.0.0.1") is True

    def test_valid_broadcast(self):
        assert validate_ipv4("255.255.255.255") is True

    def test_valid_zero(self):
        assert validate_ipv4("0.0.0.0") is True

    def test_invalid_ipv6(self):
        assert validate_ipv4("::1") is False

    def test_invalid_empty(self):
        assert validate_ipv4("") is False

    def test_invalid_string(self):
        assert validate_ipv4("abc") is False

    def test_invalid_out_of_range(self):
        assert validate_ipv4("999.0.0.1") is False

    def test_invalid_missing_octet(self):
        assert validate_ipv4("192.168.1") is False


class TestValidateIpv6:
    def test_valid_loopback(self):
        assert validate_ipv6("::1") is True

    def test_valid_full(self):
        assert validate_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True

    def test_valid_compressed(self):
        assert validate_ipv6("2001:db8::1") is True

    def test_valid_all_zeros(self):
        assert validate_ipv6("::") is True

    def test_invalid_ipv4(self):
        assert validate_ipv6("8.8.8.8") is False

    def test_invalid_empty(self):
        assert validate_ipv6("") is False

    def test_invalid_string(self):
        assert validate_ipv6("not-ipv6") is False

    def test_invalid_too_many_groups(self):
        assert validate_ipv6("1:2:3:4:5:6:7:8:9") is False


class TestValidatePort:
    def test_valid_http(self):
        assert validate_port(80) is True

    def test_valid_https(self):
        assert validate_port(443) is True

    def test_valid_min(self):
        assert validate_port(1) is True

    def test_valid_max(self):
        assert validate_port(65535) is True

    def test_invalid_zero(self):
        assert validate_port(0) is False

    def test_invalid_above_max(self):
        assert validate_port(65536) is False

    def test_invalid_negative(self):
        assert validate_port(-1) is False

    def test_invalid_large(self):
        assert validate_port(99999) is False

    def test_valid_privileged_boundary(self):
        assert validate_port(1024) is True

    def test_valid_common_ssh(self):
        assert validate_port(22) is True


class TestResolveHostname:
    def test_resolves_localhost(self):
        result = resolve_hostname("localhost")
        assert result == "127.0.0.1"

    def test_returns_none_for_invalid(self):
        result = resolve_hostname("this.domain.absolutely.does.not.exist.invalid")
        assert result is None

    def test_returns_string_on_success(self):
        result = resolve_hostname("localhost")
        assert isinstance(result, str)
