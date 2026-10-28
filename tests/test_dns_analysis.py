"""Deterministic DNS resolution, validation, health, and comparison tests."""

import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import dns.exception
import dns.resolver
import pytest

from nadzoring.dns_lookup import compare, health, utils, validation
from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig


@pytest.mark.parametrize("asynchronous", [False, True])
def test_resolver_configuration(asynchronous):
    """Configure both resolver implementations without issuing queries."""
    factory = utils.create_async_resolver if asynchronous else utils.create_resolver
    resolver = factory("192.0.2.1")
    assert resolver.nameservers == ["192.0.2.1"]
    assert resolver.timeout == 5
    assert resolver.lifetime == 10
    resolver = factory(timeout_config=TimeoutConfig(read=2, lifetime=3))
    assert resolver.timeout == 2
    assert resolver.lifetime == 3


@pytest.mark.parametrize(
    "rtype,answers,expected",
    [
        (
            "MX",
            [SimpleNamespace(preference=10, exchange="mail.example.com.")],
            ["10 mail.example.com"],
        ),
        ("TXT", [SimpleNamespace(strings=[b"hello", "world", 1])], ["helloworld1"]),
        (
            "SOA",
            [
                SimpleNamespace(
                    mname="ns",
                    rname="host",
                    serial=1,
                    refresh=2,
                    retry=3,
                    expire=4,
                    minimum=5,
                )
            ],
            ["ns host 1 2 3 4 5"],
        ),
        ("NS", ["ns.example.com."], ["ns.example.com"]),
    ],
)
def test_record_extraction(rtype, answers, expected):
    """Format type-specific DNS data."""
    assert utils.extract_records(answers, rtype) == expected


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "failure,error",
    [
        (None, None),
        (dns.resolver.NoAnswer(), "No records of requested type"),
        (dns.resolver.NXDOMAIN(), "Domain does not exist"),
        (dns.exception.Timeout(), "Query timeout"),
        (ValueError("invalid"), "Resolver error"),
    ],
)
def test_timed_resolution(monkeypatch, asynchronous, failure, error):
    """Return records, TTL, timing, and structured resolver errors."""

    class Answers(list):
        rrset = SimpleNamespace(ttl=120)

    resolve = (
        AsyncMock(return_value=Answers(["192.0.2.1"])) if asynchronous else Mock(return_value=Answers(["192.0.2.1"]))
    )
    resolve.side_effect = failure
    factory = "create_async_resolver" if asynchronous else "create_resolver"
    monkeypatch.setattr(utils, factory, Mock(return_value=SimpleNamespace(resolve=resolve)))
    if asynchronous:
        result = asyncio.run(utils.resolve_with_timer_async("example.com", include_ttl=True))
    else:
        result = utils.resolve_with_timer("example.com", include_ttl=True)
    assert result["error"] == error
    if error is None:
        assert result["records"] == ["192.0.2.1"]
        assert result["ttl"] == 120
        assert result["response_time"] >= 0
    else:
        assert result["records"] == []


def test_resolution_lifetime_timeout(monkeypatch):
    """Convert lifetime expiry at the timeout context boundary."""

    @contextmanager
    def expired(_):
        raise OperationTimeoutError("expired")
        yield

    monkeypatch.setattr(utils, "timeout_context", expired)
    assert utils.resolve_with_timer("example.com")["error"] == "Operation exceeded lifetime timeout"
    servers = utils.get_public_dns_servers()
    servers.clear()
    assert "8.8.8.8" in utils.get_public_dns_servers()


@pytest.mark.parametrize(
    "score,status",
    [
        (100, "healthy"),
        (80, "healthy"),
        (79, "degraded"),
        (50, "degraded"),
        (49, "unhealthy"),
    ],
)
def test_health_status_boundaries(score, status):
    """Respect exact status thresholds."""
    assert validation.determine_status(score) == status


def test_dns_record_validation():
    """Detect malformed MX and missing SPF/DKIM configuration."""
    result = validation.validate_mx_records(["10 mail", "10 backup", "invalid", ""])
    assert result["valid"] is False
    assert len(result["issues"]) == 3
    result = validation.validate_txt_records(["unrelated", "v=spf1", "v=DKIM1"])
    assert result["valid"] is False
    assert len(result["warnings"]) == 1
    assert len(result["issues"]) == 1
    assert validation.validate_txt_records(["v=spf1 -all", "v=DKIM1; p=key"])["valid"] is True


@pytest.mark.parametrize(
    "rtype,data,score",
    [
        ("A", {"error": "No records of requested type"}, 70),
        ("A", {"error": "Query timeout"}, 50),
        ("A", {"records": []}, 80),
        ("A", {"records": ["192.0.2.1"]}, 100),
        ("MX", {"records": ["10 mail", "10 backup", "invalid"]}, 60),
        ("TXT", {"records": ["v=spf1", "v=DKIM1", "unrelated"]}, 70),
        ("TXT", {"records": ["v=spf1 ~all", "v=DKIM1; p=key"]}, 100),
    ],
)
def test_dns_record_scoring(rtype, data, score):
    """Apply penalties and collect explanatory diagnostics."""
    accumulator = {"issues": [], "warnings": []}
    assert validation.calculate_record_score(rtype, data, accumulator) == score
    assert bool(accumulator["issues"] or accumulator["warnings"]) == (score != 100)


@pytest.mark.parametrize("domain,count", [("example.com", 5), ("www.example.com", 6)])
def test_dns_health(monkeypatch, domain, count):
    """Exclude apex CNAME records from the health average."""
    resolve = Mock(return_value={"records": ["value"], "error": None})
    monkeypatch.setattr(health, "resolve_with_timer", resolve)
    result = health.health_check_dns(domain)
    assert resolve.call_count == count
    assert result["record_scores"]["CNAME"] == 100
    assert result["status"] == "healthy"


def test_detailed_dns_check(monkeypatch):
    """Include record validation and preserve query failures."""

    def resolve(domain, rtype, *args, **kwargs):
        records = {"MX": ["10 mail"], "TXT": ["v=spf1 -all"]}.get(rtype, [])
        return {
            "records": records,
            "response_time": 1.5,
            "error": None if records else "No records of requested type",
        }

    monkeypatch.setattr(health, "resolve_with_timer", resolve)
    result = health.check_dns("example.com", validate_mx=True, validate_txt=True)
    assert result["validations"]["mx"]["valid"]
    assert result["validations"]["txt"]["valid"]
    assert result["response_times"]["MX"] == 1.5
    assert "A" in result["errors"]


def test_dns_server_comparison(monkeypatch):
    """Compare records against the baseline and report TTL differences."""

    def resolve(domain, rtype, server, **kwargs):
        return {
            "records": [server if rtype == "A" else "same"],
            "ttl": 100 if server == "first" else 50,
        }

    monkeypatch.setattr(compare, "resolve_with_timer", resolve)
    progress = Mock()
    result = compare.compare_dns_servers("example.com", ["first", "second"], ["A", "NS"], progress)
    assert progress.call_count == 4
    assert len(result["differences"]) == 1
    assert result["differences"][0]["ttl_difference"] == 50
    assert result["servers"]["first"]["A"]["differs"] is False
    assert compare._calculate_ttl_difference(None, 50) is None
