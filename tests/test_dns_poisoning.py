"""DNS poisoning comparisons and classification tests."""

import pytest

from nadzoring.dns_lookup import poisoning as poison


def test_ip_ownership_and_patterns():
    """Classify known providers, address families, geography, and invalid IPs."""
    assert poison.get_ip_owner("8.8.8.8") == "Google"
    assert poison.get_ip_owner("::1") == "Unknown"
    assert poison.get_ip_owner("invalid") == "Unknown"
    assert poison.get_ip_owner("192.168.1.1") == "Unknown"
    assert poison.is_likely_cdn([]) == (False, "Unknown", 0)
    assert poison.is_likely_cdn(["192.168.1.1"]) == (False, "Unknown", 0)
    assert poison.is_likely_cdn(["8.8.8.8", "8.8.4.4"])[0]
    assert poison._analyze_ip_patterns([]) == {}
    result = poison._analyze_ip_patterns(["8.8.8.8", "1.1.1.1", "3.1.1.1", "192.168.1.1", "::1", "invalid"])
    assert result["ipv4"] == 4
    assert result["ipv6"] == 1
    assert result["private"] >= 1
    assert result["reserved"] >= 1
    assert set(result["countries"]) == {"US", "EU", "Asia", "Unknown"}


@pytest.mark.parametrize(
    "control,test,kind,severity",
    [
        ({"error": None}, {"error": "NXDOMAIN"}, "error_mismatch", "high"),
        ({"error": None}, {"error": "timeout"}, "error_mismatch", "medium"),
        ({"error": "timeout"}, {"error": "timeout"}, None, None),
        ({"records": ["8.8.8.8"]}, {"records": ["8.8.4.4"]}, "cdn_variation", "info"),
        ({"records": ["8.8.8.8"]}, {"records": ["1.1.1.1"]}, "record_mismatch", "high"),
        ({"records": ["8.8.8.8"]}, {"records": ["8.8.8.8", "1.1.1.1"]}, "record_mismatch", "medium"),
        ({"records": ["8.8.8.8"], "ttl": 1}, {"records": ["8.8.8.8"], "ttl": 4000}, "ttl_mismatch", "low"),
        ({"records": []}, {"records": []}, None, None),
    ],
)
def test_poisoning_comparisons(control, test, kind, severity):
    """Distinguish errors, CDN variation, record mismatches, and TTL drift."""
    result = poison._compare_results(control, test, "1.1.1.1")
    if kind is None:
        assert result is None
    else:
        assert result["type"] == kind
        assert result["severity"] == severity


@pytest.mark.parametrize(
    "confidence,poisoned,cdn,level",
    [
        (100, False, False, "NONE"),
        (90, True, True, "SUSPICIOUS"),
        (70, True, True, "LOW"),
        (90, True, False, "CRITICAL"),
        (60, True, False, "HIGH"),
        (30, True, False, "MEDIUM"),
        (10, True, False, "LOW"),
    ],
)
def test_poisoning_levels(confidence, poisoned, cdn, level):
    """Map confidence to severity with CDN-specific handling."""
    assert poison._determine_poisoning_level(confidence, poisoned=poisoned, cdn_detected=cdn) == level


def test_poisoning_orchestration(monkeypatch):
    """Query all servers, skip the control, and assemble analysis metrics."""
    records = {
        "control": ["8.8.8.8"],
        "same": ["8.8.8.8"],
        "cdn": ["8.8.4.4"],
        "different": ["1.1.1.1"],
        "error": [],
    }

    def resolve(domain, rtype, server, **kwargs):
        return {"records": records[server], "error": "timeout" if server == "error" else None, "ttl": 100}

    monkeypatch.setattr(poison, "resolve_with_timer", resolve)
    monkeypatch.setattr(poison, "get_public_dns_servers", lambda: list(records))
    result = poison.check_dns_poisoning("example.com", control_server="control", additional_types=["MX"])
    assert result["test_servers_count"] == 4
    assert result["mismatches"] == 1
    assert result["cdn_variations"] == 1
    assert result["severity"] == {"high": 1, "medium": 1, "low": 0, "info": 1}
    assert "MX" in result["additional_records"]
    assert result["cdn_detected"] is True
    assert poison._get_additional_records("example.com", None, "control", None) is None


def test_poisoning_metrics():
    """Handle empty results and CDN-adjusted confidence."""
    assert poison._calculate_metrics({}, {"records": []}, 0, 0)["confidence"] == 0
    metrics = poison._calculate_metrics({"a": {"records": ["8.8.8.8"]}}, {"records": ["8.8.4.4"]}, 1, 0)
    assert metrics["cdn_detected"] is True
    assert metrics["confidence"] == 0
    assert metrics["poisoned"] is False
