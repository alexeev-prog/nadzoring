# tests/test_network_base/test_traceroute.py
"""Tests for nadzoring.network_base.traceroute — 100% coverage."""

from subprocess import TimeoutExpired

import pytest

from nadzoring.network_base.traceroute import (
    TraceHop,
    _is_permission_error,
    _parse_linux_traceroute,
    _parse_windows_tracert,
    _run_linux_traceroute,
    _run_tracepath,
    _run_windows_tracert,
    _stream_process,
    traceroute,
)


def test_is_permission_error_operation_not_permitted():
    assert _is_permission_error("Operation not permitted") is True


def test_is_permission_error_permission_denied():
    assert _is_permission_error("permission denied") is True


def test_is_permission_error_case_insensitive():
    assert _is_permission_error("PERMISSION DENIED") is True


def test_is_permission_error_false_for_other():
    assert _is_permission_error("command not found") is False


def test_is_permission_error_empty():
    assert _is_permission_error("") is False


def test_parse_linux_empty():
    assert _parse_linux_traceroute("") == []


def test_parse_linux_single_hop():
    raw = " 1  router (192.168.1.1)  1.234 ms\n"
    hops = _parse_linux_traceroute(raw)
    assert len(hops) == 1
    assert hops[0].hop == 1
    assert hops[0].ip == "192.168.1.1"
    assert hops[0].host == "router"
    assert hops[0].rtt_ms == [pytest.approx(1.234)]


def test_parse_linux_star_hop():
    raw = " 3  * * *\n"
    hops = _parse_linux_traceroute(raw)
    assert len(hops) == 1
    assert hops[0].hop == 3
    assert hops[0].host is None
    assert hops[0].ip is None
    assert hops[0].rtt_ms == [None]


def test_parse_linux_multiple_rtt():
    raw = " 2  host (1.2.3.4)  5.0 ms  5.1 ms  4.9 ms\n"
    hops = _parse_linux_traceroute(raw)
    assert len(hops[0].rtt_ms) == 3


def test_parse_linux_multiple_hops():
    raw = " 1  gw (10.0.0.1)  0.5 ms\n 2  * * *\n 3  8.8.8.8 (8.8.8.8)  15.2 ms\n"
    hops = _parse_linux_traceroute(raw)
    assert len(hops) == 3
    assert [h.hop for h in hops] == [1, 2, 3]


def test_parse_linux_blank_lines_skipped():
    raw = "\n 1  gw (10.0.0.1)  1.0 ms\n\n"
    assert len(_parse_linux_traceroute(raw)) == 1


def test_parse_linux_no_host_match_fallback_to_parts():
    raw = " 1  192.168.1.1  2.0 ms\n"
    hops = _parse_linux_traceroute(raw)
    assert len(hops) == 1
    assert hops[0].ip is not None or hops[0].host is not None


def test_parse_linux_rtt_value_error_appends_none():
    raw = " 1  host (1.2.3.4)  abc ms\n"
    hops = _parse_linux_traceroute(raw)
    assert hops[0].rtt_ms == [None]


def test_parse_linux_precision():
    raw = " 1  host (1.2.3.4)  123.456 ms\n"
    hops = _parse_linux_traceroute(raw)
    assert hops[0].rtt_ms[0] == pytest.approx(123.456)


def test_parse_windows_empty():
    assert _parse_windows_tracert("") == []


def test_parse_windows_single_hop():
    raw = "  1     1 ms    1 ms    1 ms  192.168.1.1\n"
    hops = _parse_windows_tracert(raw)
    assert len(hops) == 1
    assert hops[0].hop == 1
    assert hops[0].ip == "192.168.1.1"


def test_parse_windows_three_rtt():
    raw = "  1    10 ms    11 ms    12 ms  10.0.0.1\n"
    hops = _parse_windows_tracert(raw)
    assert len(hops[0].rtt_ms) == 3


def test_parse_windows_star_hop():
    raw = "  2     *        *        *     Request timed out.\n"
    hops = _parse_windows_tracert(raw)
    assert len(hops) == 1
    assert hops[0].hop == 2
    assert hops[0].rtt_ms == [None]


def test_parse_windows_header_skipped():
    raw = "Tracing route to example.com\n  1  1 ms  1 ms  1 ms  1.2.3.4\n"
    assert len(_parse_windows_tracert(raw)) == 1


def test_parse_windows_hop_number():
    raw = "  5    20 ms    21 ms    20 ms  8.8.8.8\n"
    assert _parse_windows_tracert(raw)[0].hop == 5


def test_parse_windows_ip_none_when_no_match():
    raw = "  1     * * *\n"
    hops = _parse_windows_tracert(raw)
    assert hops[0].host is None
    assert hops[0].ip is None


def test_parse_windows_host_fallback_to_ip():
    raw = "  1     1 ms     1 ms     1 ms  10.0.0.1\n"
    hops = _parse_windows_tracert(raw)
    assert hops[0].ip == "10.0.0.1"


def test_stream_process_success(mocker):
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.return_value = ("output text", "")
    mock_proc.__enter__ = mocker.MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("nadzoring.network_base.traceroute.Popen", return_value=mock_proc)

    stdout, stderr = _stream_process("echo hello", wall_timeout=5.0)
    assert stdout == "output text"
    assert stderr == ""


def test_stream_process_timeout_returns_partial(mocker):
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.side_effect = [
        TimeoutExpired("cmd", 5),
        ("partial", ""),
    ]
    mock_proc.__enter__ = mocker.MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("nadzoring.network_base.traceroute.Popen", return_value=mock_proc)

    stdout, stderr = _stream_process("traceroute 8.8.8.8", wall_timeout=1.0)
    assert stdout == "partial"
    mock_proc.kill.assert_called_once()


def test_run_linux_traceroute_success(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=(" 1  gw (10.0.0.1)  1.0 ms\n", ""),
    )
    hops = _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=False)
    assert len(hops) == 1
    assert hops[0].hop == 1


def test_run_linux_traceroute_empty_output(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", ""),
    )
    result = _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=False)
    assert result == []


def test_run_linux_traceroute_with_sudo(mocker):
    mock_sp = mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=(" 1  gw (10.0.0.1)  1.0 ms\n", ""),
    )
    _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=True)
    cmd = mock_sp.call_args[0][0]
    assert cmd.startswith("sudo ")


def test_run_linux_traceroute_permission_error_returns_empty(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", "Operation not permitted"),
    )
    result = _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=False)
    assert result == []


def test_run_linux_traceroute_no_output_with_error_returns_empty(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", "some error"),
    )
    result = _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=False)
    assert result == []


def test_run_linux_traceroute_command_not_found_falls_back_to_tracepath(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", "not found"),
    )
    mock_tp = mocker.patch(
        "nadzoring.network_base.traceroute._run_tracepath",
        return_value=[],
    )
    _run_linux_traceroute("8.8.8.8", max_hops=5, per_hop_timeout=2.0, use_sudo=False)
    mock_tp.assert_called_once()


def test_run_tracepath_success(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=(" 1:  10.0.0.1  1.000ms\n", ""),
    )
    result = _run_tracepath("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    assert isinstance(result, list)


def test_run_tracepath_empty_output(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", ""),
    )
    result = _run_tracepath("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    assert result == []


def test_run_tracepath_failure_returns_empty(mocker):
    mocker.patch(
        "nadzoring.network_base.traceroute._stream_process",
        return_value=("", "command not found"),
    )
    result = _run_tracepath("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    assert result == []


def test_run_windows_tracert_success(mocker):
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.return_value = (
        "  1     1 ms     1 ms     1 ms  192.168.1.1\n".encode("cp866"),
        b"",
    )
    mock_proc.__enter__ = mocker.MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("nadzoring.network_base.traceroute.Popen", return_value=mock_proc)

    result = _run_windows_tracert("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    assert isinstance(result, list)
    assert len(result) == 1


def test_run_windows_tracert_empty_output(mocker):
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.return_value = (b"", b"")
    mock_proc.__enter__ = mocker.MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("nadzoring.network_base.traceroute.Popen", return_value=mock_proc)

    result = _run_windows_tracert("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    assert result == []


def test_run_windows_tracert_timeout_returns_partial(mocker):
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.side_effect = [
        TimeoutExpired("tracert", 10),
        (b"  1     1 ms     1 ms     1 ms  10.0.0.1\n", b""),
    ]
    mock_proc.__enter__ = mocker.MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("nadzoring.network_base.traceroute.Popen", return_value=mock_proc)

    result = _run_windows_tracert("8.8.8.8", max_hops=5, per_hop_timeout=2.0)
    mock_proc.kill.assert_called_once()
    assert isinstance(result, list)


def test_traceroute_linux(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.traceroute._run_linux_traceroute", return_value=[])
    traceroute("8.8.8.8")
    mock.assert_called_once()


def test_traceroute_windows(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Windows")
    mock = mocker.patch("nadzoring.network_base.traceroute._run_windows_tracert", return_value=[])
    traceroute("8.8.8.8")
    mock.assert_called_once()


def test_traceroute_unsupported_os_returns_empty(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Darwin")
    assert traceroute("8.8.8.8") == []


def test_traceroute_passes_max_hops(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.traceroute._run_linux_traceroute", return_value=[])
    traceroute("8.8.8.8", max_hops=10)
    assert mock.call_args[1]["max_hops"] == 10


def test_traceroute_passes_per_hop_timeout(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.traceroute._run_linux_traceroute", return_value=[])
    traceroute("8.8.8.8", per_hop_timeout=5.0)
    assert mock.call_args[1]["per_hop_timeout"] == 5.0


def test_traceroute_passes_use_sudo(mocker):
    mocker.patch("nadzoring.network_base.traceroute.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.traceroute._run_linux_traceroute", return_value=[])
    traceroute("8.8.8.8", use_sudo=True)
    assert mock.call_args[1]["use_sudo"] is True


def test_tracehop_default_rtt_empty():
    hop = TraceHop(hop=1, host="gw", ip="10.0.0.1")
    assert hop.rtt_ms == []


def test_tracehop_none_values():
    hop = TraceHop(hop=2, host=None, ip=None, rtt_ms=[None])
    assert hop.host is None
    assert hop.ip is None
    assert hop.rtt_ms == [None]
