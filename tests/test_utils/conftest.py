"""Shared pytest fixtures for nadzoring tests."""

import pytest


@pytest.fixture
def dns_record_data():
    return [
        {
            "domain": "example.com",
            "records": {
                "A": {"records": ["1.2.3.4", "5.6.7.8"], "ttl": 300},
                "MX": {"records": ["mail.example.com"], "ttl": 3600},
                "TXT": {"error": "TIMEOUT"},
            },
        }
    ]


@pytest.fixture
def health_data():
    return {
        "domain": "example.com",
        "score": 75,
        "status": "degraded",
        "issues": ["missing SPF"],
        "warnings": ["low TTL"],
        "record_scores": {"A": 95, "MX": 60, "DKIM": 30},
    }


@pytest.fixture
def comparison_data():
    return {
        "servers": {
            "8.8.8.8": {
                "A": {"records": ["1.2.3.4"], "response_time": 12, "differs": False},
                "MX": {
                    "records": ["mail.example.com"],
                    "response_time": 15,
                    "differs": True,
                },
            },
            "1.1.1.1": {
                "A": {"records": ["1.2.3.4"], "response_time": 8, "differs": False},
            },
        }
    }
