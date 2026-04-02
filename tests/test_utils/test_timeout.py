# tests/test_utils/test_timeout.py
"""Tests for nadzoring.utils.timeout — 100% coverage."""

import signal
import socket

import pytest

from nadzoring.utils.timeout import (
    OperationTimeoutError,
    TimeoutConfig,
    _raise_timeout_error,
    configure_socket_with_timeouts,
    timeout_context,
    with_lifetime_timeout,
)


class TestTimeoutConfig:
    def test_default_connect(self):
        assert TimeoutConfig().connect == 5.0

    def test_default_read(self):
        assert TimeoutConfig().read == 10.0

    def test_default_lifetime(self):
        assert TimeoutConfig().lifetime == 120.0

    def test_custom_values(self):
        cfg = TimeoutConfig(connect=1.0, read=2.0, lifetime=30.0)
        assert cfg.connect == 1.0
        assert cfg.read == 2.0
        assert cfg.lifetime == 30.0

    def test_apply_to_socket_sets_read_timeout(self, mocker):
        mock_sock = mocker.MagicMock(spec=socket.socket)
        cfg = TimeoutConfig(read=7.5)
        cfg.apply_to_socket(mock_sock)
        mock_sock.settimeout.assert_called_once_with(7.5)


class TestOperationTimeoutError:
    def test_default_message(self):
        exc = OperationTimeoutError()
        assert "lifetime" in str(exc).lower() or "timeout" in str(exc).lower()

    def test_custom_message(self):
        exc = OperationTimeoutError("custom msg")
        assert str(exc) == "custom msg"

    def test_is_timeout_error(self):
        assert issubclass(OperationTimeoutError, TimeoutError)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(OperationTimeoutError):
            raise OperationTimeoutError("boom")

    def test_caught_as_timeout_error(self):
        with pytest.raises(TimeoutError):
            raise OperationTimeoutError()


class TestRaiseTimeoutError:
    def test_raises_operation_timeout_error(self):
        with pytest.raises(OperationTimeoutError):
            _raise_timeout_error(signal.SIGALRM, None)


class TestTimeoutContext:
    def test_normal_execution_passes_through(self):
        cfg = TimeoutConfig(lifetime=5.0)
        with timeout_context(cfg):
            result = 1 + 1
        assert result == 2

    def test_non_timeout_exception_propagates(self):
        cfg = TimeoutConfig(lifetime=5.0)
        with pytest.raises(ValueError), timeout_context(cfg):
            raise ValueError("inner error")

    def test_operation_timeout_error_propagates(self):
        cfg = TimeoutConfig(lifetime=5.0)
        with pytest.raises(OperationTimeoutError), timeout_context(cfg):
            raise OperationTimeoutError("timed out")

    def test_no_sigalrm_still_yields(self, mocker):
        cfg = TimeoutConfig(lifetime=5.0)
        mocker.patch("nadzoring.utils.timeout.signal", spec=["signal", "alarm"])
        mocker.patch("nadzoring.utils.timeout.signal.SIGALRM", None, create=True)
        executed = []
        with timeout_context(cfg):
            executed.append(True)
        assert executed

    def test_lifetime_none_skips_alarm(self, mocker):
        cfg = TimeoutConfig(lifetime=None)
        mock_alarm = mocker.patch("nadzoring.utils.timeout.signal.alarm")
        with timeout_context(cfg):
            pass
        mock_alarm.assert_not_called()

    def test_alarm_set_and_cancelled_success(self, mocker):
        mock_alarm = mocker.patch("nadzoring.utils.timeout.signal.alarm")
        mocker.patch("nadzoring.utils.timeout.signal.signal")
        cfg = TimeoutConfig(lifetime=3.0)
        with timeout_context(cfg):
            pass
        assert mock_alarm.call_count >= 2
        calls = [c[0][0] for c in mock_alarm.call_args_list]
        assert 3 in calls
        assert 0 in calls

    def test_alarm_set_and_cancelled_exception(self, mocker):
        mock_alarm = mocker.patch("nadzoring.utils.timeout.signal.alarm")
        mocker.patch("nadzoring.utils.timeout.signal.signal")
        cfg = TimeoutConfig(lifetime=3.0)
        with pytest.raises(RuntimeError), timeout_context(cfg):
            raise RuntimeError("fail")
        calls = [c[0][0] for c in mock_alarm.call_args_list]
        assert 3 in calls
        assert 0 in calls

    def test_windows_no_sigalrm_fallback(self, mocker):
        import nadzoring.utils.timeout as t_mod

        mocker.patch.object(t_mod, "signal", spec=[])
        cfg = TimeoutConfig(lifetime=2.0)
        executed = []
        with timeout_context(cfg):
            executed.append(True)
        assert executed


class TestConfigureSocketWithTimeouts:
    def test_connect_mode_sets_connect_timeout(self, mocker):
        mock_sock = mocker.MagicMock(spec=socket.socket)
        cfg = TimeoutConfig(connect=3.0, read=10.0)
        configure_socket_with_timeouts(mock_sock, cfg, connect_mode=True)
        mock_sock.settimeout.assert_called_once_with(3.0)

    def test_read_mode_sets_read_timeout(self, mocker):
        mock_sock = mocker.MagicMock(spec=socket.socket)
        cfg = TimeoutConfig(connect=3.0, read=10.0)
        configure_socket_with_timeouts(mock_sock, cfg, connect_mode=False)
        mock_sock.settimeout.assert_called_once_with(10.0)

    def test_default_connect_mode_is_false(self, mocker):
        mock_sock = mocker.MagicMock(spec=socket.socket)
        cfg = TimeoutConfig(read=7.0)
        configure_socket_with_timeouts(mock_sock, cfg)
        mock_sock.settimeout.assert_called_once_with(7.0)


class TestWithLifetimeTimeout:
    def test_decorated_function_executes(self):
        cfg = TimeoutConfig(lifetime=5.0)

        @with_lifetime_timeout(cfg)
        def fn():
            return 42

        assert fn() == 42

    def test_decorated_function_passes_args(self):
        cfg = TimeoutConfig(lifetime=5.0)

        @with_lifetime_timeout(cfg)
        def fn(x, y):
            return x + y

        assert fn(3, 4) == 7

    def test_decorated_function_raises_on_timeout(self, mocker):
        mocker.patch("nadzoring.utils.timeout.signal.signal")

        def fake_alarm(n):
            if n > 0:
                raise OperationTimeoutError("forced timeout")

        mocker.patch("nadzoring.utils.timeout.signal.alarm", side_effect=fake_alarm)
        cfg = TimeoutConfig(lifetime=1.0)

        @with_lifetime_timeout(cfg)
        def slow():
            return "done"

        with pytest.raises(OperationTimeoutError):
            slow()

    def test_preserves_function_name(self):
        cfg = TimeoutConfig(lifetime=5.0)

        @with_lifetime_timeout(cfg)
        def my_special_function():
            pass

        assert my_special_function.__name__ == "my_special_function"

    def test_inner_exception_propagates(self):
        cfg = TimeoutConfig(lifetime=5.0)

        @with_lifetime_timeout(cfg)
        def fn():
            raise ValueError("inner")

        with pytest.raises(ValueError, match="inner"):
            fn()

    def test_lifetime_none_no_timeout(self):
        cfg = TimeoutConfig(lifetime=None)

        @with_lifetime_timeout(cfg)
        def fn():
            return 42

        assert fn() == 42
