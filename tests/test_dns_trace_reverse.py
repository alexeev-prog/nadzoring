"""Reverse DNS and delegation chain tests without network access."""

from types import SimpleNamespace
from unittest.mock import Mock

import dns.exception
import dns.name
import dns.resolver
import dns.rrset
import pytest

from nadzoring.dns_lookup import reverse, trace
from nadzoring.utils.timeout import TimeoutConfig


@pytest.mark.parametrize(
    "failure,error",
    [
        (None, None),
        (dns.resolver.NoAnswer(), "No PTR record"),
        (dns.resolver.NXDOMAIN(), "No reverse DNS"),
        (dns.exception.Timeout(), "Query timeout"),
        (ValueError(), "Invalid IP address"),
        (RuntimeError(), "Resolver error"),
    ],
)
def test_reverse_dns(monkeypatch, failure, error):
    """Normalize PTR names and return expected errors."""
    resolve = Mock(return_value=["host.example.com."], side_effect=failure)
    monkeypatch.setattr(reverse, "create_resolver", Mock(return_value=SimpleNamespace(resolve=resolve)))
    result = reverse.reverse_dns("192.0.2.1")
    assert result["error"] == error
    assert result["hostname"] == (None if error else "host.example.com")


@pytest.mark.parametrize(
    "failure,error",
    [
        (None, None),
        (dns.resolver.NoAnswer(), "No answer"),
        (dns.resolver.NXDOMAIN(), "Domain does not exist"),
        (dns.exception.Timeout(), "Timeout"),
        (RuntimeError("failed"), "failed"),
    ],
)
def test_nameserver_query(monkeypatch, failure, error):
    """Distinguish query failures from successful responses."""
    monkeypatch.setattr(
        trace,
        "create_resolver",
        Mock(return_value=SimpleNamespace(resolve=Mock(return_value=["192.0.2.1"], side_effect=failure))),
    )
    answers, elapsed, actual = trace._query_nameserver("example.com", "192.0.2.53", TimeoutConfig())
    assert actual == error
    assert answers == (None if error else ["192.0.2.1"])
    assert (elapsed is None) == (error == "Timeout")


@pytest.mark.parametrize("mode", ["success", "fallback", "unresolved", "failed"])
def test_delegation_lookup(monkeypatch, mode):
    """Follow NS records, including socket fallback and malformed responses."""
    authority = [
        dns.rrset.from_text("example.com", 60, "IN", "A", "192.0.2.1"),
        dns.rrset.from_text("example.com", 60, "IN", "NS", "ns.example.com."),
    ]
    monkeypatch.setattr(
        trace.dns.query,
        "udp",
        Mock(
            return_value=SimpleNamespace(authority=authority),
            side_effect=OSError("failed") if mode == "failed" else None,
        ),
    )
    monkeypatch.setattr(
        trace.dns.resolver,
        "resolve",
        Mock(
            return_value=["192.0.2.53"],
            side_effect=OSError() if mode != "success" else None,
        ),
    )
    monkeypatch.setattr(
        trace.socket,
        "gethostbyname",
        Mock(
            return_value="192.0.2.54",
            side_effect=OSError() if mode == "unresolved" else None,
        ),
    )
    hop = trace._create_hop("root")
    result = trace._get_delegation_info(dns.name.from_text("example.com"), "root", hop, TimeoutConfig())
    assert result == {"success": "192.0.2.53", "fallback": "192.0.2.54"}.get(mode)
    if mode == "failed":
        assert hop["error"] == "Delegation error: failed"
    else:
        assert "Delegation to ns.example.com." in hop["records"][0]


@pytest.mark.parametrize("mode", ["complete", "loop", "stop", "limit"])
def test_trace_chain(monkeypatch, mode):
    """Terminate on an answer, a loop, missing delegation, or the hop limit."""
    monkeypatch.setattr(
        trace,
        "_query_nameserver",
        Mock(
            return_value=(
                ["192.0.2.1"] if mode == "complete" else None,
                1.0,
                "No answer" if mode == "stop" else None,
            )
        ),
    )
    monkeypatch.setattr(trace, "_MAX_HOPS", 3)
    monkeypatch.setattr(
        trace,
        "_get_delegation_info",
        Mock(
            side_effect={
                "complete": [],
                "loop": ["second", trace._ROOT_NAMESERVER],
                "stop": [None],
                "limit": ["second", "third", "fourth"],
            }[mode]
        ),
    )
    result = trace.trace_dns("example.com")
    if mode == "complete":
        assert result["final_answer"]["records"] == ["192.0.2.1"]
    elif mode == "loop":
        assert result["hops"][-1]["error"] == "Loop detected"
    elif mode == "stop":
        assert result["hops"][-1]["next"] == "No further delegation"
        assert result["hops"][-1]["error"] == "No answer"
    else:
        assert len(result["hops"]) == 3
