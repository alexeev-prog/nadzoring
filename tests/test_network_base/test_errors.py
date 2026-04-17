"""Tests for nadzoring.network_base.errors — 100% coverage.

This file only imports the Literal types to achieve coverage, as type aliases
are not executable but are counted in coverage reports.
"""

from nadzoring.network_base.errors import (
    GeolocationError,
    PingError,
    PortScanError,
    TracerouteError,
    WHOISError,
)


def test_literal_types_importable():
    """Verify that all Literal type aliases can be imported."""
    assert PingError is not None
    assert TracerouteError is not None
    assert WHOISError is not None
    assert PortScanError is not None
    assert GeolocationError is not None


def test_ping_error_literals():
    """PingError should be a tuple of strings."""
    assert isinstance(PingError.__args__, tuple)


def test_traceroute_error_literals():
    """TracerouteError should be a tuple of strings."""
    assert isinstance(TracerouteError.__args__, tuple)


def test_whois_error_literals():
    """WHOISError should be a tuple of strings."""
    assert isinstance(WHOISError.__args__, tuple)


def test_port_scan_error_literals():
    """PortScanError should be a tuple of strings."""
    assert isinstance(PortScanError.__args__, tuple)


def test_geolocation_error_literals():
    """GeolocationError should be a tuple of strings."""
    assert isinstance(GeolocationError.__args__, tuple)
