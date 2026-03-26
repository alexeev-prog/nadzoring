"""Tests for nadzoring.network_base.connections."""

from unittest.mock import patch

from nadzoring.network_base.connections import (
    ConnectionEntry,
    _filter_entries,
    _parse_netstat_output,
    _parse_ss_output,
    get_connections,
)

# ---------------------------------------------------------------------------
# _parse_ss_output
# ---------------------------------------------------------------------------

SS_SAMPLE = """\
Netid  State      Recv-Q Send-Q  Local Address:Port   Peer Address:Port
tcp    LISTEN     0      128     0.0.0.0:22            0.0.0.0:*         users:(("sshd",pid=1234,fd=3))
tcp    ESTAB      0      0       192.168.1.100:54321   93.184.216.34:80  users:(("curl",pid=5678,fd=5))
udp    UNCONN     0      0       0.0.0.0:5353          0.0.0.0:*
"""


class TestParseSsOutput:
    def test_parses_tcp_listen(self):
        entries = _parse_ss_output(SS_SAMPLE)
        listen = next(e for e in entries if e.state == "LISTEN")
        assert listen.protocol == "tcp"
        assert "22" in listen.local_address

    def test_parses_established(self):
        entries = _parse_ss_output(SS_SAMPLE)
        estab = next(e for e in entries if e.state == "ESTAB")
        assert estab.protocol == "tcp"

    def test_parses_udp_entry(self):
        entries = _parse_ss_output(SS_SAMPLE)
        udp = next(e for e in entries if e.protocol == "udp")
        assert udp is not None

    def test_pid_extracted_from_users_field(self):
        entries = _parse_ss_output(SS_SAMPLE)
        estab = next(e for e in entries if e.state == "ESTAB")
        assert estab.pid == "5678"

    def test_process_name_extracted(self):
        entries = _parse_ss_output(SS_SAMPLE)
        estab = next(e for e in entries if e.state == "ESTAB")
        assert estab.process == "curl"

    def test_empty_string_returns_empty(self):
        assert _parse_ss_output("") == []

    def test_header_only_returns_empty(self):
        assert _parse_ss_output("Netid  State  Recv-Q Send-Q  Local Peer\n") == []

    def test_correct_entry_count(self):
        entries = _parse_ss_output(SS_SAMPLE)
        assert len(entries) == 3

    def test_remote_address_captured(self):
        entries = _parse_ss_output(SS_SAMPLE)
        estab = next(e for e in entries if e.state == "ESTAB")
        assert "80" in estab.remote_address or "93" in estab.remote_address


# ---------------------------------------------------------------------------
# _parse_netstat_output
# ---------------------------------------------------------------------------

NETSTAT_SAMPLE = """\
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    127.0.0.1:3306         0.0.0.0:0              LISTENING       1111
  TCP    192.168.1.100:52000    93.184.216.34:443      ESTABLISHED     2222
  UDP    0.0.0.0:5353           *:*                                    3333
  UDP    0.0.0.0:137            *:*                                    4444
"""


class TestParseNetstatOutput:
    def test_tcp_listening_entry(self):
        entries = _parse_netstat_output(NETSTAT_SAMPLE)
        listen = next(e for e in entries if e.state == "LISTENING")
        assert listen.protocol == "TCP"
        assert listen.pid == "1111"

    def test_tcp_established_entry(self):
        entries = _parse_netstat_output(NETSTAT_SAMPLE)
        estab = next(e for e in entries if e.state == "ESTABLISHED")
        assert estab.local_address == "192.168.1.100:52000"

    def test_udp_entries_state_empty(self):
        entries = _parse_netstat_output(NETSTAT_SAMPLE)
        udp_entries = [e for e in entries if e.protocol == "UDP"]
        assert all(e.state == "" for e in udp_entries)

    def test_non_protocol_lines_ignored(self):
        entries = _parse_netstat_output(NETSTAT_SAMPLE)
        assert all(e.protocol in {"TCP", "UDP"} for e in entries)

    def test_empty_input_returns_empty(self):
        assert _parse_netstat_output("") == []

    def test_four_entries_total(self):
        assert len(_parse_netstat_output(NETSTAT_SAMPLE)) == 4

    def test_pid_captured_for_udp(self):
        entries = _parse_netstat_output(NETSTAT_SAMPLE)
        udp = next(e for e in entries if e.protocol == "UDP")
        assert udp.pid in {"3333", "4444"}


# ---------------------------------------------------------------------------
# _filter_entries
# ---------------------------------------------------------------------------


class TestFilterEntries:
    def _entries(self):
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

    def test_filter_tcp_only(self):
        result = _filter_entries(self._entries(), protocol="tcp", state_filter=None)
        assert all(e.protocol.lower() == "tcp" for e in result)
        assert len(result) == 2

    def test_filter_udp_only(self):
        result = _filter_entries(self._entries(), protocol="udp", state_filter=None)
        assert all(e.protocol.lower() == "udp" for e in result)
        assert len(result) == 1

    def test_filter_all_returns_everything(self):
        result = _filter_entries(self._entries(), protocol="all", state_filter=None)
        assert len(result) == 3

    def test_state_filter_listen(self):
        result = _filter_entries(self._entries(), protocol="all", state_filter="LISTEN")
        assert len(result) == 1
        assert result[0].state == "LISTEN"

    def test_state_filter_case_insensitive(self):
        result = _filter_entries(self._entries(), protocol="all", state_filter="listen")
        assert len(result) == 1

    def test_combined_protocol_and_state_filter(self):
        result = _filter_entries(self._entries(), protocol="tcp", state_filter="ESTABLISHED")
        assert len(result) == 1
        assert result[0].remote_address.startswith("1.2.3.4")

    def test_no_match_returns_empty(self):
        result = _filter_entries(self._entries(), protocol="tcp", state_filter="TIME_WAIT")
        assert result == []


# ---------------------------------------------------------------------------
# get_connections — dispatcher
# ---------------------------------------------------------------------------


class TestGetConnections:
    @patch("nadzoring.network_base.connections.system", return_value="Linux")
    @patch("nadzoring.network_base.connections._get_linux_connections", return_value=[])
    def test_linux_calls_linux_impl(self, mock_linux, mock_sys):
        get_connections()
        mock_linux.assert_called_once()

    @patch("nadzoring.network_base.connections.system", return_value="Windows")
    @patch("nadzoring.network_base.connections._get_windows_connections", return_value=[])
    def test_windows_calls_windows_impl(self, mock_win, mock_sys):
        get_connections()
        mock_win.assert_called_once()

    @patch("nadzoring.network_base.connections.system", return_value="Darwin")
    def test_unsupported_os_returns_empty(self, mock_sys):
        assert get_connections() == []

    @patch("nadzoring.network_base.connections.system", return_value="Linux")
    @patch("nadzoring.network_base.connections._get_linux_connections")
    def test_protocol_kwarg_forwarded(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        get_connections(protocol="tcp")
        _, kwargs = mock_linux.call_args
        assert kwargs["protocol"] == "tcp"

    @patch("nadzoring.network_base.connections.system", return_value="Linux")
    @patch("nadzoring.network_base.connections._get_linux_connections")
    def test_state_filter_kwarg_forwarded(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        get_connections(state_filter="LISTEN")
        _, kwargs = mock_linux.call_args
        assert kwargs["state_filter"] == "LISTEN"

    @patch("nadzoring.network_base.connections.system", return_value="Linux")
    @patch("nadzoring.network_base.connections._get_linux_connections")
    def test_include_process_forwarded(self, mock_linux, mock_sys):
        mock_linux.return_value = []
        get_connections(include_process=False)
        _, kwargs = mock_linux.call_args
        assert kwargs["include_process"] is False

    @patch("nadzoring.network_base.connections.system", return_value="Linux")
    @patch("nadzoring.network_base.connections.check_output", side_effect=FileNotFoundError)
    def test_ss_not_found_returns_empty(self, mock_co, mock_sys):
        result = get_connections()
        assert result == []
