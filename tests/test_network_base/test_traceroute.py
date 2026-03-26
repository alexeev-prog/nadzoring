"""Tests for nadzoring.network_base.traceroute."""

from unittest.mock import patch

import pytest

from nadzoring.network_base.traceroute import (
    TraceHop,
    _parse_linux_traceroute,
    _parse_windows_tracert,
    traceroute,
)

# ---------------------------------------------------------------------------
# _parse_linux_traceroute
# ---------------------------------------------------------------------------


class TestParseLinuxTraceroute:
    def test_single_hop_with_rtt(self):
        raw = " 1  router (192.168.1.1)  1.234 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 1
        assert hops[0].hop == 1
        assert hops[0].ip == "192.168.1.1"
        assert hops[0].host == "router"
        assert hops[0].rtt_ms == [pytest.approx(1.234)]

    def test_timeout_hop_star(self):
        raw = " 3  * * *\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 1
        assert hops[0].hop == 3
        assert hops[0].host is None
        assert hops[0].ip is None
        assert hops[0].rtt_ms == [None]

    def test_multiple_hops(self):
        raw = " 1  gw (10.0.0.1)  0.5 ms\n 2  * * *\n 3  8.8.8.8 (8.8.8.8)  15.2 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 3
        assert hops[0].hop == 1
        assert hops[1].hop == 2
        assert hops[2].hop == 3

    def test_multiple_rtt_values(self):
        raw = " 2  host (1.2.3.4)  5.0 ms  5.1 ms  4.9 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops[0].rtt_ms) == 3

    def test_empty_input_returns_empty_list(self):
        assert _parse_linux_traceroute("") == []

    def test_non_hop_lines_skipped(self):
        raw = "traceroute to 8.8.8.8 (8.8.8.8), 30 hops max\n 1  router (10.0.0.1)  1.0 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 1

    def test_hop_without_hostname(self):
        # IP only (no hostname in parentheses)
        raw = " 1  192.168.1.1  2.0 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 1
        assert hops[0].ip is not None or hops[0].host is not None

    def test_hop_numbers_sequential(self):
        raw = " 1  a (1.1.1.1)  1.0 ms\n 2  b (2.2.2.2)  2.0 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert [h.hop for h in hops] == [1, 2]

    def test_blank_lines_skipped(self):
        raw = "\n 1  gw (10.0.0.1)  1.0 ms\n\n"
        hops = _parse_linux_traceroute(raw)
        assert len(hops) == 1

    def test_rtt_precision_preserved(self):
        raw = " 1  host (1.2.3.4)  123.456 ms\n"
        hops = _parse_linux_traceroute(raw)
        assert hops[0].rtt_ms[0] == pytest.approx(123.456)


# ---------------------------------------------------------------------------
# _parse_windows_tracert
# ---------------------------------------------------------------------------


class TestParseWindowsTracert:
    def test_single_hop(self):
        raw = "  1     1 ms    1 ms    1 ms  192.168.1.1\n"
        hops = _parse_windows_tracert(raw)
        assert len(hops) == 1
        assert hops[0].hop == 1
        assert hops[0].ip == "192.168.1.1"

    def test_timeout_hop(self):
        raw = "  2     *        *        *     Request timed out.\n"
        hops = _parse_windows_tracert(raw)
        # Star-only check; "Request timed out." has no digits except hop num
        assert len(hops) == 1
        assert hops[0].hop == 2

    def test_multiple_rtt(self):
        raw = "  1    10 ms    11 ms    12 ms  10.0.0.1\n"
        hops = _parse_windows_tracert(raw)
        assert len(hops[0].rtt_ms) == 3

    def test_empty_input(self):
        assert _parse_windows_tracert("") == []

    def test_header_lines_skipped(self):
        raw = "Tracing route to example.com\n\n  1     1 ms     1 ms     1 ms  192.168.1.1\n"
        hops = _parse_windows_tracert(raw)
        assert len(hops) == 1

    def test_hop_number_correct(self):
        raw = "  5    20 ms    21 ms    20 ms  8.8.8.8\n"
        hops = _parse_windows_tracert(raw)
        assert hops[0].hop == 5


# ---------------------------------------------------------------------------
# traceroute — dispatcher
# ---------------------------------------------------------------------------


class TestTracerouteDispatcher:
    @patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    @patch("nadzoring.network_base.traceroute._run_linux_traceroute", return_value=[])
    def test_linux_calls_linux_impl(self, mock_linux, mock_sys):
        traceroute("8.8.8.8")
        mock_linux.assert_called_once()

    @patch("nadzoring.network_base.traceroute.system", return_value="Windows")
    @patch("nadzoring.network_base.traceroute._run_windows_tracert", return_value=[])
    def test_windows_calls_windows_impl(self, mock_win, mock_sys):
        traceroute("8.8.8.8")
        mock_win.assert_called_once()

    @patch("nadzoring.network_base.traceroute.system", return_value="Darwin")
    def test_unsupported_os_returns_empty_list(self, mock_sys):
        result = traceroute("8.8.8.8")
        assert result == []

    @patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    @patch("nadzoring.network_base.traceroute._run_linux_traceroute")
    def test_passes_max_hops_to_linux(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        traceroute("8.8.8.8", max_hops=10)
        _, kwargs = mock_linux.call_args
        assert kwargs["max_hops"] == 10

    @patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    @patch("nadzoring.network_base.traceroute._run_linux_traceroute")
    def test_passes_per_hop_timeout_to_linux(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        traceroute("8.8.8.8", per_hop_timeout=5.0)
        _, kwargs = mock_linux.call_args
        assert kwargs["per_hop_timeout"] == 5.0

    @patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    @patch("nadzoring.network_base.traceroute._run_linux_traceroute")
    def test_passes_use_sudo_to_linux(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        traceroute("8.8.8.8", use_sudo=True)
        _, kwargs = mock_linux.call_args
        assert kwargs["use_sudo"] is True

    @patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    @patch("nadzoring.network_base.traceroute._run_linux_traceroute")
    def test_returns_list_of_trace_hops(self, mock_linux, mock_sys):
        mock_linux.return_value = [TraceHop(hop=1, host="gw", ip="10.0.0.1", rtt_ms=[1.0])]
        result = traceroute("8.8.8.8")
        assert isinstance(result, list)
        assert isinstance(result[0], TraceHop)


# ---------------------------------------------------------------------------
# TraceHop dataclass
# ---------------------------------------------------------------------------


class TestTraceHop:
    def test_defaults(self):
        hop = TraceHop(hop=1, host="gw", ip="10.0.0.1")
        assert hop.rtt_ms == []

    def test_none_host_and_ip_for_timeout(self):
        hop = TraceHop(hop=2, host=None, ip=None, rtt_ms=[None])
        assert hop.host is None
        assert hop.ip is None
        assert hop.rtt_ms == [None]
