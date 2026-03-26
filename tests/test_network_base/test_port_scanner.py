"""Tests for nadzoring.network_base.port_scanner."""

import socket
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from nadzoring.network_base.port_scanner import (
    COMMON_PORTS,
    PortResult,
    ScanConfig,
    ScanResult,
    get_ports_from_mode,
    resolve_target,
    scan_ports,
)

# ---------------------------------------------------------------------------
# resolve_target
# ---------------------------------------------------------------------------


class TestResolveTarget:
    def test_valid_ipv4_returned_unchanged(self):
        assert resolve_target("192.168.1.1") == "192.168.1.1"

    def test_valid_ipv6_returned_unchanged(self):
        assert resolve_target("::1") == "::1"

    @patch("nadzoring.network_base.port_scanner.socket.gethostbyname")
    def test_hostname_resolved(self, mock_ghbn):
        mock_ghbn.return_value = "93.184.216.34"
        assert resolve_target("example.com") == "93.184.216.34"
        mock_ghbn.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.port_scanner.socket.gethostbyname")
    def test_unresolvable_hostname_returns_none(self, mock_ghbn):
        mock_ghbn.side_effect = socket.gaierror
        assert resolve_target("invalid.local.xxxx") is None

    def test_loopback_returned_unchanged(self):
        assert resolve_target("127.0.0.1") == "127.0.0.1"


# ---------------------------------------------------------------------------
# get_ports_from_mode
# ---------------------------------------------------------------------------


class TestGetPortsFromMode:
    def _cfg(self, mode, **kwargs):
        return ScanConfig(targets=["127.0.0.1"], mode=mode, **kwargs)

    def test_fast_returns_common_ports_sorted(self):
        ports = get_ports_from_mode(self._cfg("fast"))
        assert ports == sorted(COMMON_PORTS)

    def test_fast_no_duplicates(self):
        ports = get_ports_from_mode(self._cfg("fast"))
        assert len(ports) == len(set(ports))

    def test_full_returns_1_to_65535(self):
        ports = get_ports_from_mode(self._cfg("full"))
        assert ports[0] == 1
        assert ports[-1] == 65535
        assert len(ports) == 65535

    def test_custom_with_explicit_list(self):
        ports = get_ports_from_mode(self._cfg("custom", custom_ports=[443, 80, 22, 80]))
        assert sorted({443, 80, 22}) == ports

    def test_custom_with_port_range(self):
        ports = get_ports_from_mode(self._cfg("custom", port_range=(100, 110)))
        assert ports == list(range(100, 111))

    def test_custom_port_range_clamped_min(self):
        ports = get_ports_from_mode(self._cfg("custom", port_range=(0, 5)))
        assert ports[0] == 1

    def test_custom_port_range_clamped_max(self):
        ports = get_ports_from_mode(self._cfg("custom", port_range=(65530, 70000)))
        assert ports[-1] == 65535

    def test_custom_no_ports_or_range_returns_empty(self):
        ports = get_ports_from_mode(self._cfg("custom"))
        assert ports == []

    def test_unknown_mode_returns_empty(self):
        cfg = ScanConfig(targets=["x"], mode="fast")  # type: ignore[arg-type]
        # Force an unknown mode via direct attribute mutation
        cfg.mode = "unknown"  # type: ignore[assignment]
        assert get_ports_from_mode(cfg) == []


# ---------------------------------------------------------------------------
# ScanResult properties
# ---------------------------------------------------------------------------


class TestScanResultProperties:
    def _make_result(self):
        t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        t1 = datetime(2024, 1, 1, 0, 0, 5, tzinfo=UTC)
        return ScanResult(
            target="192.168.1.1",
            target_ip="192.168.1.1",
            start_time=t0,
            end_time=t1,
            results={
                80: PortResult(port=80, state="open", service="http"),
                443: PortResult(port=443, state="open", service="https"),
                22: PortResult(port=22, state="filtered"),
                25: PortResult(port=25, state="closed"),
            },
        )

    def test_duration_seconds(self):
        result = self._make_result()
        assert result.duration == pytest.approx(5.0)

    def test_open_ports_only_open(self):
        result = self._make_result()
        assert sorted(result.open_ports) == [80, 443]

    def test_open_ports_excludes_filtered(self):
        result = self._make_result()
        assert 22 not in result.open_ports

    def test_open_ports_excludes_closed(self):
        result = self._make_result()
        assert 25 not in result.open_ports

    def test_empty_results_open_ports_empty(self):
        t = datetime(2024, 1, 1, tzinfo=UTC)
        r = ScanResult(target="x", target_ip="x", start_time=t, end_time=t)
        assert r.open_ports == []


# ---------------------------------------------------------------------------
# scan_ports — high-level integration (mocked internals)
# ---------------------------------------------------------------------------


class TestScanPorts:
    def _make_config(self, **kwargs):
        defaults = dict(targets=["192.168.1.1"], mode="fast", max_workers=10, grab_banner=False)
        defaults.update(kwargs)
        return ScanConfig(**defaults)

    @patch("nadzoring.network_base.port_scanner.resolve_target", return_value=None)
    def test_unresolvable_target_returns_empty(self, mock_rt):
        result = scan_ports(self._make_config(targets=["bad.host"]))
        assert result == []

    @patch("nadzoring.network_base.port_scanner.resolve_target", return_value="192.168.1.1")
    @patch("nadzoring.network_base.port_scanner._scan_target_ports")
    def test_returns_scan_result_per_target(self, mock_scan, mock_rt):
        fake_result = MagicMock(spec=ScanResult)
        mock_scan.return_value = fake_result
        results = scan_ports(self._make_config(targets=["host1"]))
        assert results == [fake_result]

    @patch("nadzoring.network_base.port_scanner.resolve_target", return_value="1.1.1.1")
    @patch("nadzoring.network_base.port_scanner._scan_target_ports")
    def test_multiple_targets_each_scanned(self, mock_scan, mock_rt):
        mock_scan.return_value = MagicMock(spec=ScanResult)
        results = scan_ports(self._make_config(targets=["h1", "h2", "h3"]))
        assert len(results) == 3
        assert mock_scan.call_count == 3

    def test_custom_mode_no_ports_returns_empty(self):
        cfg = self._make_config(mode="custom")
        result = scan_ports(cfg)
        assert result == []

    @patch("nadzoring.network_base.port_scanner.resolve_target")
    @patch("nadzoring.network_base.port_scanner._scan_target_ports")
    def test_mixed_resolvable_skips_failed(self, mock_scan, mock_rt):
        mock_rt.side_effect = lambda t: None if t == "bad" else "1.2.3.4"
        mock_scan.return_value = MagicMock(spec=ScanResult)
        results = scan_ports(self._make_config(targets=["good", "bad"]))
        assert len(results) == 1


# ---------------------------------------------------------------------------
# PortResult defaults
# ---------------------------------------------------------------------------


class TestPortResultDefaults:
    def test_default_state_can_be_filtered(self):
        r = PortResult(port=80, state="filtered")
        assert r.state == "filtered"

    def test_default_service_unknown(self):
        r = PortResult(port=80, state="open")
        assert r.service == "unknown"

    def test_default_banner_none(self):
        r = PortResult(port=80, state="open")
        assert r.banner is None

    def test_default_response_time_none(self):
        r = PortResult(port=80, state="open")
        assert r.response_time is None
