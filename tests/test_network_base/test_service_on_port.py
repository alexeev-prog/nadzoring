"""Tests for nadzoring.network_base.service_on_port."""

from unittest.mock import patch

from nadzoring.network_base.service_on_port import get_service_on_port


class TestGetServiceOnPort:
    """Tests for get_service_on_port function."""

    # --- System lookup succeeds ---

    def test_well_known_http(self):
        assert get_service_on_port(80) == "http"

    def test_well_known_ssh(self):
        assert get_service_on_port(22) == "ssh"

    def test_well_known_https(self):
        assert get_service_on_port(443) == "https"

    def test_well_known_ftp(self):
        assert get_service_on_port(21) == "ftp"

    def test_well_known_smtp(self):
        assert get_service_on_port(25) == "smtp"

    def test_well_known_dns(self):
        assert get_service_on_port(53) == "domain"

    # --- System lookup fails → fallback table ---

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_fallback_mysql(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(3306) == "mysql"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_fallback_postgresql(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(5432) == "postgresql"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_fallback_redis(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(6379) == "redis"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_fallback_mongodb(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(27017) == "mongodb"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_fallback_http_alt(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(8080) == "http-alt"

    # --- System lookup fails, port not in fallback → "Unknown" ---

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_unknown_port_returns_Unknown(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(9999) == "Unknown"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_zero_port_returns_Unknown(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(0) == "Unknown"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_max_port_returns_Unknown(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert get_service_on_port(65535) == "Unknown"

    # --- OverflowError / TypeError from bad input ---

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_overflow_error_falls_back(self, mock_gsb):
        mock_gsb.side_effect = OverflowError
        result = get_service_on_port(99999)
        assert isinstance(result, str)

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_type_error_falls_back(self, mock_gsb):
        mock_gsb.side_effect = TypeError
        result = get_service_on_port(-1)
        assert isinstance(result, str)

    # --- Return type ---

    def test_return_is_str(self):
        assert isinstance(get_service_on_port(80), str)

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_unknown_return_is_str(self, mock_gsb):
        mock_gsb.side_effect = OSError
        assert isinstance(get_service_on_port(12345), str)

    # --- getservbyport is called with the correct argument ---

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_calls_getservbyport_with_port(self, mock_gsb):
        mock_gsb.return_value = "smtp"
        get_service_on_port(25)
        mock_gsb.assert_called_once_with(25)
