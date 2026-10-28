"""Security analysis tests with DNS, HTTP, sockets, and clocks isolated."""

import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

from nadzoring.security import email_security as email
from nadzoring.security import http_headers as headers
from nadzoring.security import ssl_monitor
from nadzoring.security import subdomain_scan as scan
from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig


def test_txt_dns_chunks(monkeypatch):
    """Join TXT chunks returned by the resolver."""
    resolve = Mock(return_value=[SimpleNamespace(strings=[b"v=spf1 ", b"-all"])])
    monkeypatch.setattr(email.dns.resolver, "resolve", resolve)
    assert email._query_txt("example.com") == ["v=spf1 -all"]
    resolve.assert_called_once_with("example.com", "TXT", lifetime=5)
    assert email._join_txt_chunks(" plain ") == "plain"


@pytest.mark.parametrize("fallback", ["dig", "nslookup", "failed"])
def test_txt_system_fallbacks(monkeypatch, fallback):
    """Exercise both system-tool fallbacks and total lookup failure."""
    monkeypatch.setattr(email.dns.resolver, "resolve", Mock(side_effect=OSError))
    outputs = {
        "dig": ['\n"v=spf1 " "-all"\n'],
        "nslookup": [FileNotFoundError(), 'ignored\n text = "v=spf1 " "-all"'],
        "failed": [subprocess.TimeoutExpired("dig", 10), FileNotFoundError()],
    }
    monkeypatch.setattr(email.subprocess, "check_output", Mock(side_effect=outputs[fallback]))
    assert email._query_txt("example.com") == ([] if fallback == "failed" else ["v=spf1 -all"])


@pytest.mark.parametrize(
    "records,qualifier,issue",
    [
        ([], None, "No SPF"),
        (["v=spf1 -all"], "-", None),
        (["v=spf1 +all", "v=spf1 ~all"], "+", "Multiple SPF"),
        (["v=spf1 all"], "+", "+all allows"),
        (["v=spf1 " + "include:example.com " * 11], None, "Exceeds 10"),
    ],
)
def test_spf_analysis(monkeypatch, records, qualifier, issue):
    """Validate SPF qualifiers, duplicate records, and lookup limits."""
    monkeypatch.setattr(email, "_query_txt", lambda _: records)
    result = email._analyse_spf("example.com")
    assert result.all_qualifier == qualifier
    assert result.found == bool(records)
    if issue:
        assert any(issue in item for item in result.issues)
    else:
        assert not result.issues


@pytest.mark.parametrize("found", [False, True])
def test_dkim_analysis(monkeypatch, found):
    """Record discovered selectors and report missing signing keys."""
    monkeypatch.setattr(email, "_query_txt", lambda _: ["v=DKIM1; p=abc"] if found else [])
    result = email._analyse_dkim("example.com")
    assert result.found is found
    assert len(result.selectors_checked) == len(email._DKIM_SELECTORS)
    assert bool(result.issues) is not found


@pytest.mark.parametrize(
    "record,policy,pct,issue",
    [
        (None, None, None, "No DMARC"),
        ("v=DMARC1; ignored", None, None, "Missing policy"),
        ("v=DMARC1; p=none; pct=20", "none", 20, "only 20%"),
        ("v=DMARC1; p=reject; pct=invalid", "reject", None, "Invalid pct"),
        (
            "v=DMARC1; p=reject; sp=quarantine; pct=100; rua=mailto:a, mailto:b; ruf=mailto:c",
            "reject",
            100,
            None,
        ),
    ],
)
def test_dmarc_analysis(monkeypatch, record, policy, pct, issue):
    """Parse DMARC tags and flag missing, invalid, and weak policies."""
    monkeypatch.setattr(email, "_query_txt", lambda _: [record] if record else [])
    result = email._analyse_dmarc("example.com")
    assert result.policy == policy
    assert result.pct == pct
    if issue:
        assert any(issue in item for item in result.issues)
    else:
        assert result.rua == ["mailto:a", "mailto:b"]
        assert result.ruf == ["mailto:c"]
        assert result.subdomain_policy == "quarantine"
        assert not result.issues


def test_email_summary(monkeypatch):
    """Aggregate protocol scores and issues into the public result."""
    monkeypatch.setattr(email, "_query_txt", lambda _: [])
    result = email.check_email_security("example.com")
    assert result["domain"] == "example.com"
    assert result["overall_score"] == 0
    assert len(result["all_issues"]) == 3


def test_http_headers_analysis(monkeypatch):
    """Analyse case-insensitive headers and preserve final redirect metadata."""
    response = SimpleNamespace(
        url="https://example.com/final",
        status_code=200,
        headers={
            "strict-transport-security": "max-age=100",
            "X-XSS-Protection": "0",
            "server": "test",
        },
    )
    get = Mock(return_value=response)
    monkeypatch.setattr(headers.requests, "get", get)
    result = headers.check_http_security_headers("example.com", verify_ssl=False)
    assert result["error"] is None
    assert result["url"] == response.url
    assert result["leaking"] == {"Server": "test"}
    assert result["deprecated"] == ["X-XSS-Protection"]
    assert "Content-Security-Policy" in result["missing"]
    assert result["score"] == round(2 / len(headers._SECURITY_HEADERS) * 100)
    assert get.call_args.args == ("https://example.com",)
    assert get.call_args.kwargs["verify"] is False
    monkeypatch.setattr(headers, "_SECURITY_HEADERS", {})
    assert headers._score_headers({}, []) == 0


@pytest.mark.parametrize(
    "exception,error",
    [
        (OperationTimeoutError, "Operation lifetime timeout"),
        (requests.exceptions.Timeout, "Request timeout"),
        (requests.exceptions.SSLError, "SSL verification failed"),
        (requests.exceptions.ConnectionError, "Connection refused"),
        (requests.exceptions.TooManyRedirects, "Too many redirects"),
        (requests.exceptions.RequestException, "Invalid URL"),
    ],
)
def test_http_headers_failures(monkeypatch, exception, error):
    """Convert expected request failures into structured errors."""
    monkeypatch.setattr(headers.requests, "get", Mock(side_effect=exception("failed")))
    result = headers.check_http_security_headers("https://example.com", timeout_config=TimeoutConfig())
    assert result["error"] == error
    assert result["status_code"] is None


@pytest.mark.parametrize("failure", [None, requests.RequestException(), ValueError()])
def test_ct_discovery(monkeypatch, failure):
    """Normalize and deduplicate certificate transparency names."""
    response = Mock()
    response.json.return_value = [
        {"name_value": "*.api.example.com\nexample.com\nother.net\napi.example.com"},
        {},
    ]
    if failure:
        response.json.side_effect = failure
    monkeypatch.setattr(scan.requests, "get", Mock(return_value=response))
    assert scan._fetch_ct_subdomains("example.com", TimeoutConfig()) == (set() if failure else {"api.example.com"})


@pytest.mark.parametrize("failure", [None, TimeoutError(), scan.socket.gaierror()])
def test_subdomain_probe(monkeypatch, failure):
    """Probe through fake sockets without contacting any host."""
    sock = Mock()
    sock.connect.side_effect = failure
    monkeypatch.setattr(scan.socket, "socket", Mock(return_value=sock))
    monkeypatch.setattr(scan.socket, "gethostbyname", lambda _: "192.0.2.1")
    result = scan._probe_subdomain("api.example.com", TimeoutConfig())
    assert result == (None if failure else {"subdomain": "api.example.com", "ip": "192.0.2.1"})


def test_subdomain_scan(monkeypatch, tmp_path):
    """Merge sources, ignore failed futures, and sort live results."""
    wordlist = tmp_path / "words"
    wordlist.write_text("api\n www \n\nfailed\nmissing\n", encoding="utf-8")
    assert scan._load_wordlist(wordlist) == ["api", "www", "failed", "missing"]
    assert scan._load_wordlist(tmp_path / "absent") == []
    monkeypatch.setattr(scan, "_fetch_ct_subdomains", lambda *_: {"api.example.com"})

    def probe(sub, _):
        if sub.startswith("failed"):
            raise RuntimeError("probe failure")
        if sub.startswith("missing"):
            return None
        return {"subdomain": sub, "ip": "192.0.2.1"}

    monkeypatch.setattr(scan, "_probe_subdomain", probe)
    results = scan.scan_subdomains("example.com", wordlist_path=str(wordlist))
    assert [result["subdomain"] for result in results] == [
        "api.example.com",
        "www.example.com",
    ]
    assert [result["source"] for result in results] == ["ct_log", "brute_force"]
    assert len(scan.scan_subdomains("example.com", wordlist_path="", timeout_config=TimeoutConfig())) == 1
    monkeypatch.setattr(scan, "_DEFAULT_WORDLIST", ("www",))
    assert len(scan.scan_subdomains("example.com")) == 2


def test_ssl_monitor_cycles(monkeypatch):
    """Alert on expiry, failed checks, and certificate changes across cycles."""
    check = Mock(
        side_effect=[
            {"status": "warning", "remaining_days": 2, "expiry_date": "old"},
            {"status": "expired", "expiry_date": "new"},
            {"status": "error", "error": "failed"},
            RuntimeError("unexpected"),
        ]
    )
    monkeypatch.setattr(ssl_monitor, "check_ssl_certificate_safe", check)
    sleep = Mock()
    monkeypatch.setattr(ssl_monitor.time, "sleep", sleep)
    monitor = ssl_monitor.SSLMonitor(["example.com"], interval=5)
    callback = Mock()
    monitor.set_alert_callback(callback)
    assert len(monitor.run_cycles(4)) == 3
    assert callback.call_count == 4
    assert len(monitor.history()) == 3
    assert sleep.call_count == 3
    snapshot = monitor.history()
    snapshot.clear()
    assert len(monitor.history()) == 3
    ssl_monitor._default_alert("example.com", "test")


def test_ssl_monitor_infinite_loop(monkeypatch):
    """Stop indefinite monitoring through an external interruption."""
    monitor = ssl_monitor.SSLMonitor([])
    monkeypatch.setattr(ssl_monitor.time, "sleep", Mock(side_effect=KeyboardInterrupt))
    with pytest.raises(KeyboardInterrupt):
        monitor.run()
