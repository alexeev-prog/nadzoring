"""Tests for nadzoring.network_base.connections — 100% coverage."""

from subprocess import CalledProcessError

import pytest

from nadzoring.network_base.connections import (
    ConnectionEntry,
    _filter_entries,
    _get_linux_connections,
    _get_windows_connections,
    _parse_netstat_output,
    _parse_ss_output,
    get_connections,
)

# ---------------------------------------------------------------------------
# _parse_ss_output
# ---------------------------------------------------------------------------

SS_SAMPLE = (
    "Netid  State      Recv-Q Send-Q  Local Address:Port   Peer Address:Port\n"
    'tcp    LISTEN     0      128     0.0.0.0:22            0.0.0.0:*         users:(("sshd",pid=1234,fd=3))\n'
    'tcp    ESTAB      0      0       192.168.1.100:54321   93.184.216.34:80  users:(("curl",pid=5678,fd=5))\n'
    "udp    UNCONN     0      0       0.0.0.0:5353          0.0.0.0:*\n"
)


def test_ss_empty_string_returns_empty():
    assert _parse_ss_output("") == []


def test_ss_header_only_returns_empty():
    assert _parse_ss_output("Netid  State  Recv-Q Send-Q  Local Peer\n") == []


def test_ss_parses_tcp_listen():
    entries = _parse_ss_output(SS_SAMPLE)
    listen = next(e for e in entries if e.state == "LISTEN")
    assert listen.protocol == "tcp"
    assert "22" in listen.local_address


def test_ss_parses_tcp_estab():
    entries = _parse_ss_output(SS_SAMPLE)
    estab = next(e for e in entries if e.state == "ESTAB")
    assert estab.protocol == "tcp"


def test_ss_parses_udp_entry():
    entries = _parse_ss_output(SS_SAMPLE)
    udp = next(e for e in entries if e.protocol == "udp")
    assert udp is not None


def test_ss_pid_extracted():
    entries = _parse_ss_output(SS_SAMPLE)
    estab = next(e for e in entries if e.state == "ESTAB")
    assert estab.pid == "5678"


def test_ss_process_name_extracted():
    entries = _parse_ss_output(SS_SAMPLE)
    estab = next(e for e in entries if e.state == "ESTAB")
    assert estab.process == "curl"


def test_ss_entry_count():
    assert len(_parse_ss_output(SS_SAMPLE)) == 3


def test_ss_no_pid_in_line():
    raw = "Netid  State  Recv-Q Send-Q  Local  Peer\ntcp    LISTEN 0      128     0.0.0.0:80  0.0.0.0:*\n"
    entries = _parse_ss_output(raw)
    assert entries[0].pid is None
    assert entries[0].process is None


def test_ss_short_line_skipped():
    raw = (
        "Netid  State  Recv-Q Send-Q  Local  Peer\n"
        "tcp    LISTEN\n"  # too few parts
    )
    assert _parse_ss_output(raw) == []


def test_ss_remote_address_captured():
    entries = _parse_ss_output(SS_SAMPLE)
    estab = next(e for e in entries if e.state == "ESTAB")
    assert "80" in estab.remote_address or "93" in estab.remote_address


# ---------------------------------------------------------------------------
# _parse_netstat_output
# ---------------------------------------------------------------------------

NETSTAT_SAMPLE = (
    "  TCP    127.0.0.1:3306         0.0.0.0:0              LISTENING       1111\n"
    "  TCP    192.168.1.100:52000    93.184.216.34:443      ESTABLISHED     2222\n"
    "  UDP    0.0.0.0:5353           *:*                                    3333\n"
    "  UDP    0.0.0.0:137            *:*                                    4444\n"
    "  Other  line\n"
)


def test_netstat_empty_returns_empty():
    assert _parse_netstat_output("") == []


def test_netstat_tcp_listening():
    entries = _parse_netstat_output(NETSTAT_SAMPLE)
    listen = next(e for e in entries if e.state == "LISTENING")
    assert listen.protocol == "TCP"
    assert listen.pid == "1111"


def test_netstat_tcp_established():
    entries = _parse_netstat_output(NETSTAT_SAMPLE)
    estab = next(e for e in entries if e.state == "ESTABLISHED")
    assert estab.local_address == "192.168.1.100:52000"
    assert estab.pid == "2222"


def test_netstat_udp_state_empty():
    entries = _parse_netstat_output(NETSTAT_SAMPLE)
    udp = [e for e in entries if e.protocol == "UDP"]
    assert all(e.state == "" for e in udp)


def test_netstat_non_protocol_lines_ignored():
    entries = _parse_netstat_output(NETSTAT_SAMPLE)
    assert all(e.protocol in {"TCP", "UDP"} for e in entries)


def test_netstat_total_count():
    entries = _parse_netstat_output(NETSTAT_SAMPLE)
    assert len(entries) == 4


def test_netstat_tcp_too_few_parts_skipped():
    raw = "  TCP    127.0.0.1:80\n"  # only 2 parts
    assert _parse_netstat_output(raw) == []


def test_netstat_udp_too_few_parts_skipped():
    raw = "  UDP    0.0.0.0:53\n"  # only 2 parts
    assert _parse_netstat_output(raw) == []


# ---------------------------------------------------------------------------
# _filter_entries
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_entries():
    return [
        ConnectionEntry(
            protocol="tcp",
            local_address="0.0.0.0:22",
            remote_address="*:*",
            state="LISTEN",
        ),
        ConnectionEntry(
            protocol="tcp",
            local_address="192.168.1.1:443",
            remote_address="1.2.3.4:50000",
            state="ESTABLISHED",
        ),
        ConnectionEntry(
            protocol="udp",
            local_address="0.0.0.0:53",
            remote_address="*:*",
            state="UNCONN",
        ),
    ]


def test_filter_all_returns_all(sample_entries):
    assert len(_filter_entries(sample_entries, protocol="all", state_filter=None)) == 3


def test_filter_tcp_only(sample_entries):
    result = _filter_entries(sample_entries, protocol="tcp", state_filter=None)
    assert all(e.protocol.lower() == "tcp" for e in result)
    assert len(result) == 2


def test_filter_udp_only(sample_entries):
    result = _filter_entries(sample_entries, protocol="udp", state_filter=None)
    assert len(result) == 1
    assert result[0].protocol == "udp"


def test_filter_state_listen(sample_entries):
    result = _filter_entries(sample_entries, protocol="all", state_filter="LISTEN")
    assert len(result) == 1
    assert result[0].state == "LISTEN"


def test_filter_state_case_insensitive(sample_entries):
    result = _filter_entries(sample_entries, protocol="all", state_filter="listen")
    assert len(result) == 1


def test_filter_combined(sample_entries):
    result = _filter_entries(sample_entries, protocol="tcp", state_filter="ESTABLISHED")
    assert len(result) == 1


def test_filter_no_match_returns_empty(sample_entries):
    assert _filter_entries(sample_entries, protocol="tcp", state_filter="TIME_WAIT") == []


def test_filter_state_none_no_filtering(sample_entries):
    result = _filter_entries(sample_entries, protocol="all", state_filter=None)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# _get_linux_connections
# ---------------------------------------------------------------------------


def test_get_linux_connections_success(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        return_value=SS_SAMPLE.encode(),
    )
    result = _get_linux_connections(protocol="all", state_filter=None, include_process=True)
    assert isinstance(result, list)


def test_get_linux_connections_include_process_flag(mocker):
    mock_co = mocker.patch(
        "nadzoring.network_base.connections.check_output",
        return_value=b"Netid  State  Recv-Q Send-Q  Local  Peer\n",
    )
    _get_linux_connections(protocol="all", state_filter=None, include_process=True)
    call_args = mock_co.call_args[0][0]
    assert "-tunap" in " ".join(call_args)


def test_get_linux_connections_no_process_flag(mocker):
    mock_co = mocker.patch(
        "nadzoring.network_base.connections.check_output",
        return_value=b"Netid  State  Recv-Q Send-Q  Local  Peer\n",
    )
    _get_linux_connections(protocol="all", state_filter=None, include_process=False)
    call_args = mock_co.call_args[0][0]
    assert "-tuna" in " ".join(call_args)
    assert "p" not in "".join(call_args).replace("-tuna", "")


def test_get_linux_connections_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        side_effect=CalledProcessError(1, "ss"),
    )
    assert _get_linux_connections(protocol="all", state_filter=None, include_process=True) == []


def test_get_linux_connections_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_linux_connections(protocol="all", state_filter=None, include_process=True) == []


# ---------------------------------------------------------------------------
# _get_windows_connections
# ---------------------------------------------------------------------------


def test_get_windows_connections_success(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        return_value=NETSTAT_SAMPLE.encode("cp866"),
    )
    result = _get_windows_connections(protocol="all", state_filter=None)
    assert isinstance(result, list)


def test_get_windows_connections_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        side_effect=CalledProcessError(1, "netstat"),
    )
    assert _get_windows_connections(protocol="all", state_filter=None) == []


def test_get_windows_connections_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.connections.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_windows_connections(protocol="all", state_filter=None) == []


# ---------------------------------------------------------------------------
# get_connections — dispatcher
# ---------------------------------------------------------------------------


def test_get_connections_linux(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.connections._get_linux_connections", return_value=[])
    get_connections()
    mock.assert_called_once()


def test_get_connections_windows(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Windows")
    mock = mocker.patch("nadzoring.network_base.connections._get_windows_connections", return_value=[])
    get_connections()
    mock.assert_called_once()


def test_get_connections_unsupported_os(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Darwin")
    assert get_connections() == []


def test_get_connections_protocol_forwarded(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.connections._get_linux_connections", return_value=[])
    get_connections(protocol="tcp")
    _, kwargs = mock.call_args
    assert kwargs["protocol"] == "tcp"


def test_get_connections_state_filter_forwarded(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.connections._get_linux_connections", return_value=[])
    get_connections(state_filter="LISTEN")
    _, kwargs = mock.call_args
    assert kwargs["state_filter"] == "LISTEN"


def test_get_connections_include_process_forwarded(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.connections._get_linux_connections", return_value=[])
    get_connections(include_process=False)
    _, kwargs = mock.call_args
    assert kwargs["include_process"] is False


def test_get_connections_windows_protocol_forwarded(mocker):
    mocker.patch("nadzoring.network_base.connections.system", return_value="Windows")
    mock = mocker.patch("nadzoring.network_base.connections._get_windows_connections", return_value=[])
    get_connections(protocol="udp")
    _, kwargs = mock.call_args
    assert kwargs["protocol"] == "udp"
