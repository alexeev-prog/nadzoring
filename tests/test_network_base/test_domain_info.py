"""Tests for nadzoring.network_base.domain_info — 100% coverage."""

import socket

from nadzoring.network_base.domain_info import (
    _get_dns_records,
    _resolve_domain,
    get_domain_info,
)

# ---------------------------------------------------------------------------
# _resolve_domain
# ---------------------------------------------------------------------------


def test_resolve_domain_ipv4_only(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[
            (socket.AF_INET, None, None, None, ("93.184.216.34", 0)),
        ],
    )
    result = _resolve_domain("example.com")
    assert result["ipv4"] == "93.184.216.34"
    assert result["ipv6"] is None


def test_resolve_domain_ipv6_only(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[
            (
                socket.AF_INET6,
                None,
                None,
                None,
                ("2606:2800:220:1:248:1893:25c8:1946", 0, 0, 0),
            ),
        ],
    )
    result = _resolve_domain("example.com")
    assert result["ipv4"] is None
    assert result["ipv6"] == "2606:2800:220:1:248:1893:25c8:1946"


def test_resolve_domain_both(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[
            (socket.AF_INET, None, None, None, ("1.2.3.4", 0)),
            (socket.AF_INET6, None, None, None, ("::1", 0, 0, 0)),
        ],
    )
    result = _resolve_domain("example.com")
    assert result["ipv4"] == "1.2.3.4"
    assert result["ipv6"] == "::1"


def test_resolve_domain_first_ipv4_only(mocker):
    # Second AF_INET should not overwrite first
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[
            (socket.AF_INET, None, None, None, ("1.1.1.1", 0)),
            (socket.AF_INET, None, None, None, ("2.2.2.2", 0)),
        ],
    )
    result = _resolve_domain("example.com")
    assert result["ipv4"] == "1.1.1.1"


def test_resolve_domain_gaierror_returns_none_none(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        side_effect=socket.gaierror,
    )
    result = _resolve_domain("invalid.local")
    assert result["ipv4"] is None
    assert result["ipv6"] is None


def test_resolve_domain_unknown_family_skipped(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[
            (socket.AF_UNSPEC, None, None, None, ("x", 0)),
        ],
    )
    result = _resolve_domain("example.com")
    assert result["ipv4"] is None
    assert result["ipv6"] is None


# ---------------------------------------------------------------------------
# _get_dns_records
# ---------------------------------------------------------------------------


def test_get_dns_records_resolver_success(mocker):
    mock_answer = mocker.MagicMock()
    mock_answer.__iter__ = mocker.MagicMock(return_value=iter(["93.184.216.34"]))
    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        return_value=mock_answer,
    )
    records = _get_dns_records("example.com")
    assert "A" in records


def test_get_dns_records_resolver_exception_skipped(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=Exception("NXDOMAIN"),
    )
    # Falls back to socket.getaddrinfo
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[(socket.AF_INET, None, None, None, ("1.2.3.4", 0))],
    )
    records = _get_dns_records("example.com")
    assert "A" in records
    assert "1.2.3.4" in records["A"]


def test_get_dns_records_a_fallback_getaddrinfo(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=Exception("fail"),
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        side_effect=[
            [(socket.AF_INET, None, None, None, ("1.2.3.4", 0))],  # AF_INET call
            socket.gaierror,  # AF_INET6 call
        ],
    )
    records = _get_dns_records("example.com")
    assert "A" in records


def test_get_dns_records_aaaa_fallback_getaddrinfo(mocker):
    def resolver_side_effect(domain, rtype, lifetime):
        if rtype == "AAAA":
            raise Exception("no AAAA")
        raise Exception("no record")

    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=resolver_side_effect,
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        side_effect=[
            [],  # AF_INET → empty → no A added
            [(socket.AF_INET6, None, None, None, ("::1", 0, 0, 0))],  # AF_INET6
        ],
    )
    records = _get_dns_records("example.com")
    assert "AAAA" in records


def test_get_dns_records_a_fallback_gaierror(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=Exception("fail"),
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        side_effect=socket.gaierror,
    )
    records = _get_dns_records("invalid.local")
    assert "A" not in records


def test_get_dns_records_aaaa_fallback_gaierror(mocker):
    call_count = {"n": 0}

    def getaddrinfo_side(domain, port, family=None):
        call_count["n"] += 1
        if family == socket.AF_INET:
            return []
        raise socket.gaierror

    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=Exception("fail"),
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        side_effect=getaddrinfo_side,
    )
    records = _get_dns_records("example.com")
    assert "AAAA" not in records


def test_get_dns_records_empty_a_list_not_added(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.dns.resolver.resolve",
        side_effect=Exception("fail"),
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.getaddrinfo",
        return_value=[],
    )
    records = _get_dns_records("example.com")
    assert "A" not in records


# ---------------------------------------------------------------------------
# get_domain_info
# ---------------------------------------------------------------------------


def test_get_domain_info_returns_all_keys(mocker):
    mocker.patch(
        "nadzoring.network_base.domain_info.whois_lookup",
        return_value={"registrar": "ACME"},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": None},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info._get_dns_records",
        return_value={"A": ["1.2.3.4"]},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.geo_ip",
        return_value={"lat": "1", "lon": "2", "country": "US", "city": "NY"},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        return_value=("example.com", [], ["1.2.3.4"]),
    )

    result = get_domain_info("example.com")
    assert set(result.keys()) == {
        "domain",
        "whois",
        "dns",
        "geolocation",
        "reverse_dns",
    }


def test_get_domain_info_domain_field(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": None, "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})

    result = get_domain_info("example.com")
    assert result["domain"] == "example.com"


def test_get_domain_info_no_ipv4_geo_empty(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": None, "ipv6": "::1"},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})

    result = get_domain_info("example.com")
    assert result["geolocation"] == {}
    assert result["reverse_dns"] is None


def test_get_domain_info_with_ipv4_calls_geo(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})
    mock_geo = mocker.patch(
        "nadzoring.network_base.domain_info.geo_ip",
        return_value={"lat": "1", "lon": "2", "country": "US", "city": "NY"},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        return_value=("ptr.example.com", [], ["1.2.3.4"]),
    )

    result = get_domain_info("example.com")
    mock_geo.assert_called_once_with("1.2.3.4")
    assert result["geolocation"]["country"] == "US"


def test_get_domain_info_reverse_dns_resolved(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})
    mocker.patch("nadzoring.network_base.domain_info.geo_ip", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        return_value=("ptr.example.com", [], ["1.2.3.4"]),
    )

    result = get_domain_info("example.com")
    assert result["reverse_dns"] == "ptr.example.com"


def test_get_domain_info_reverse_dns_herror_suppressed(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})
    mocker.patch("nadzoring.network_base.domain_info.geo_ip", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        side_effect=socket.herror,
    )

    result = get_domain_info("example.com")
    assert result["reverse_dns"] is None


def test_get_domain_info_reverse_dns_gaierror_suppressed(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.domain_info._get_dns_records", return_value={})
    mocker.patch("nadzoring.network_base.domain_info.geo_ip", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        side_effect=socket.gaierror,
    )

    result = get_domain_info("example.com")
    assert result["reverse_dns"] is None


def test_get_domain_info_dns_structure(mocker):
    mocker.patch("nadzoring.network_base.domain_info.whois_lookup", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info._resolve_domain",
        return_value={"ipv4": "1.2.3.4", "ipv6": "::1"},
    )
    mocker.patch(
        "nadzoring.network_base.domain_info._get_dns_records",
        return_value={"A": ["1.2.3.4"]},
    )
    mocker.patch("nadzoring.network_base.domain_info.geo_ip", return_value={})
    mocker.patch(
        "nadzoring.network_base.domain_info.socket.gethostbyaddr",
        return_value=("ptr.example.com", [], ["1.2.3.4"]),
    )

    result = get_domain_info("example.com")
    assert result["dns"]["ipv4"] == "1.2.3.4"
    assert result["dns"]["ipv6"] == "::1"
    assert result["dns"]["records"]["A"] == ["1.2.3.4"]
