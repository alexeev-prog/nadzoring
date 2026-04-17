"""Tests for nadzoring.utils.result — 100% coverage."""

import pytest

from nadzoring.utils.errors import NadzoringError
from nadzoring.utils.result import is_success, unwrap, unwrap_or


class TestIsSuccess:
    def test_no_error_key_returns_true(self):
        assert is_success({"records": ["1.2.3.4"]}) is True

    def test_error_key_none_returns_true(self):
        assert is_success({"error": None, "records": []}) is True

    def test_error_key_string_returns_false(self):
        assert is_success({"error": "Domain does not exist"}) is False

    def test_error_key_empty_string_returns_false(self):
        assert is_success({"error": ""}) is False

    def test_empty_dict_returns_true(self):
        assert is_success({}) is True

    def test_error_key_zero_returns_false(self):
        assert is_success({"error": 0}) is False

    def test_error_key_false_returns_false(self):
        assert is_success({"error": False}) is False


class TestUnwrap:
    def test_no_error_returns_original_dict(self):
        original = {"records": ["1.2.3.4"]}
        result = unwrap(original)
        assert result is original

    def test_error_none_returns_original_dict(self):
        original = {"error": None, "records": []}
        result = unwrap(original)
        assert result is original

    def test_error_string_raises_nadzoring_error(self):
        with pytest.raises(NadzoringError, match="Domain does not exist"):
            unwrap({"error": "Domain does not exist"})

    def test_error_empty_string_raises_nadzoring_error(self):
        with pytest.raises(NadzoringError, match=""):
            unwrap({"error": ""})

    def test_error_non_string_raises_nadzoring_error(self):
        with pytest.raises(NadzoringError, match="42"):
            unwrap({"error": 42})

    def test_error_with_numeric_converted_to_str(self):
        with pytest.raises(NadzoringError, match="500"):
            unwrap({"error": 500})

    def test_error_with_list_converted_to_str(self):
        with pytest.raises(NadzoringError, match=r"\['a', 'b'\]"):
            unwrap({"error": ["a", "b"]})

    def test_preserves_dict_content_on_success(self):
        data = {"records": ["1.1.1.1", "2.2.2.2"], "ttl": 300}
        result = unwrap(data)
        assert result["records"] == ["1.1.1.1", "2.2.2.2"]
        assert result["ttl"] == 300


class TestUnwrapOr:
    def test_no_error_returns_original_dict(self):
        original = {"records": ["1.2.3.4"]}
        result = unwrap_or(original, [])
        assert result is original
        assert result["records"] == ["1.2.3.4"]

    def test_error_none_returns_original_dict(self):
        original = {"error": None, "records": []}
        result = unwrap_or(original, "default")
        assert result is original

    def test_error_string_returns_default(self):
        result = unwrap_or({"error": "Domain does not exist"}, [])
        assert result == []

    def test_error_empty_string_returns_default(self):
        result = unwrap_or({"error": ""}, "fallback")
        assert result == "fallback"

    def test_default_list_returns_empty_list(self):
        result = unwrap_or({"error": "timeout"}, [])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_default_dict_returns_empty_dict(self):
        result = unwrap_or({"error": "timeout"}, {})
        assert result == {}

    def test_default_none_returns_none(self):
        result = unwrap_or({"error": "error"}, None)
        assert result is None

    def test_default_zero_returns_zero(self):
        result = unwrap_or({"error": "error"}, 0)
        assert result == 0

    def test_default_string_returns_string(self):
        result = unwrap_or({"error": "error"}, "cached_value")
        assert result == "cached_value"

    def test_default_callable_not_evaluated_but_returned(self):
        default = lambda: "not executed"
        result = unwrap_or({"error": "error"}, default)
        assert result == default

    def test_preserves_dict_content_on_success_with_default(self):
        data = {"records": ["1.1.1.1"], "response_time": 42.5}
        result = unwrap_or(data, [])
        assert result["records"] == ["1.1.1.1"]
        assert result["response_time"] == 42.5
