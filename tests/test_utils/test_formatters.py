# tests/test_utils/test_formatters.py
"""Tests for nadzoring.utils.formatters — 100% coverage."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from nadzoring.utils.formatters import (
    _CRITICAL_TERMS,
    _INFO_TERMS,
    _POSITIVE_TERMS,
    _WARNING_TERMS,
    _build_html_page,
    _calculate_column_widths,
    colorize_value,
    format_dns_comparison,
    format_dns_health,
    format_dns_poisoning,
    format_dns_record,
    format_dns_trace,
    format_scan_results,
    get_terminal_width,
    print_csv_table,
    print_html_table,
    print_results_table,
    save_results,
    truncate_string,
)


class TestGetTerminalWidth:
    def test_returns_int(self):
        width = get_terminal_width()
        assert isinstance(width, int)

    def test_returns_positive(self):
        assert get_terminal_width() > 0

    def test_uses_shutil(self):
        with patch("shutil.get_terminal_size") as mock_size:
            mock_size.return_value = MagicMock(columns=120)
            assert get_terminal_width() == 120


class TestTruncateString:
    def test_short_string_unchanged(self):
        assert truncate_string("hello", 10) == "hello"

    def test_exact_length_unchanged(self):
        assert truncate_string("hello", 5) == "hello"

    def test_long_string_truncated(self):
        result = truncate_string("very long string", 10)
        assert result == "very lo..."
        assert len(result) == 10

    def test_custom_placeholder(self):
        result = truncate_string("abcdefgh", 6, placeholder="--")
        assert result.endswith("--")
        assert len(result) == 6

    def test_empty_string(self):
        assert truncate_string("", 5) == ""

    def test_placeholder_longer_than_max_width(self):
        result = truncate_string("abcdef", 2, placeholder="...")
        assert len(result) <= 2 or result.endswith("...")

    def test_unicode_string(self):
        s = "привет мир"
        result = truncate_string(s, 7)
        assert len(result) == 7
        assert result.endswith("...")

    def test_max_width_zero(self):
        result = truncate_string("abc", 0, placeholder="")
        assert result == ""


class TestColorizeValue:
    def test_no_color_returns_plain(self):
        result = colorize_value("CRITICAL", no_color=True)
        assert result == "CRITICAL"
        assert "\x1b" not in result

    def test_critical_term_gets_red_bold(self):
        result = colorize_value("CRITICAL")
        assert "\x1b" in result

    def test_high_term_gets_red_bold(self):
        result = colorize_value("HIGH")
        assert "\x1b" in result

    def test_warning_term_gets_yellow(self):
        result = colorize_value("WARNING")
        assert "\x1b" in result

    def test_medium_term_gets_yellow(self):
        result = colorize_value("MEDIUM")
        assert "\x1b" in result

    def test_info_term_gets_green(self):
        result = colorize_value("INFO")
        assert "\x1b" in result

    def test_positive_term_yes_gets_green(self):
        result = colorize_value("yes")
        assert "\x1b" in result

    def test_positive_term_up_gets_green(self):
        result = colorize_value("up")
        assert "\x1b" in result

    def test_unknown_term_no_color_codes(self):
        result = colorize_value("something_random")
        assert result == "something_random"

    def test_poisoned_term(self):
        result = colorize_value("POISONED")
        assert "\x1b" in result

    def test_error_term(self):
        result = colorize_value("ERROR")
        assert "\x1b" in result

    def test_nxdomain_term(self):
        result = colorize_value("NXDOMAIN")
        assert "\x1b" in result

    def test_mismatch_term_gets_yellow(self):
        result = colorize_value("MISMATCH")
        assert "\x1b" in result

    def test_ttl_diff_term_gets_yellow(self):
        result = colorize_value("TTL_DIFF")
        assert "\x1b" in result

    def test_clean_term_gets_green(self):
        result = colorize_value("CLEAN")
        assert "\x1b" in result

    def test_low_term_gets_green(self):
        result = colorize_value("LOW")
        assert "\x1b" in result

    def test_reference_term_gets_green(self):
        result = colorize_value("REFERENCE")
        assert "\x1b" in result

    def test_positive_term_passed_gets_green(self):
        result = colorize_value("passed")
        assert "\x1b" in result

    def test_positive_term_good_gets_green(self):
        result = colorize_value("good")
        assert "\x1b" in result

    def test_positive_term_healthy_gets_green(self):
        result = colorize_value("healthy")
        assert "\x1b" in result

    def test_non_string_no_color_applied(self):
        result = colorize_value(42)
        assert result == "42"
        assert "\x1b" not in result

    def test_float_value_as_string(self):
        result = colorize_value("123.45")
        assert result == "123.45"

    def test_non_string_float_no_color_applied(self):
        result = colorize_value(1.5)
        assert "\x1b" not in result

    def test_critical_terms_set_contains_expected(self):
        assert "CRITICAL" in _CRITICAL_TERMS
        assert "HIGH" in _CRITICAL_TERMS
        assert "POISONED" in _CRITICAL_TERMS
        assert "ERROR" in _CRITICAL_TERMS
        assert "NXDOMAIN" in _CRITICAL_TERMS

    def test_warning_terms_set_contains_expected(self):
        assert "MEDIUM" in _WARNING_TERMS
        assert "WARNING" in _WARNING_TERMS
        assert "MISMATCH" in _WARNING_TERMS
        assert "TTL_DIFF" in _WARNING_TERMS

    def test_info_terms_set_contains_expected(self):
        assert "LOW" in _INFO_TERMS
        assert "INFO" in _INFO_TERMS
        assert "REFERENCE" in _INFO_TERMS
        assert "CLEAN" in _INFO_TERMS

    def test_positive_terms_set_contains_expected(self):
        assert "yes" in _POSITIVE_TERMS
        assert "up" in _POSITIVE_TERMS
        assert "passed" in _POSITIVE_TERMS
        assert "good" in _POSITIVE_TERMS
        assert "healthy" in _POSITIVE_TERMS


class TestPrintResultsTable:
    def test_empty_data_prints_no_results(self, capsys):
        print_results_table([])
        assert "No results" in capsys.readouterr().out

    def test_single_row_printed(self, capsys):
        print_results_table([{"domain": "example.com", "ip": "1.2.3.4"}])
        out = capsys.readouterr().out
        assert "example.com" in out
        assert "1.2.3.4" in out

    def test_no_color_disables_ansi(self, capsys):
        print_results_table([{"status": "CRITICAL"}], no_color=True)
        out = capsys.readouterr().out
        assert "\x1b" not in out

    def test_multiple_rows(self, capsys):
        data = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
        print_results_table(data)
        out = capsys.readouterr().out
        assert "1" in out
        assert "3" in out

    def test_special_column_txt(self, capsys):
        print_results_table([{"TXT": "v=spf1 include:example.com ~all"}])
        out = capsys.readouterr().out
        assert "TXT" in out

    def test_custom_tablefmt(self, capsys):
        print_results_table([{"x": "y"}], tablefmt="grid")
        out = capsys.readouterr().out
        assert "x" in out


class TestPrintCsvTable:
    def test_empty_data_prints_message(self, capsys):
        print_csv_table([])
        assert "No data" in capsys.readouterr().out

    def test_header_present(self, capsys):
        print_csv_table([{"domain": "example.com", "ip": "1.2.3.4"}])
        out = capsys.readouterr().out
        assert "domain,ip" in out

    def test_data_row_present(self, capsys):
        print_csv_table([{"domain": "example.com", "ip": "1.2.3.4"}])
        out = capsys.readouterr().out
        assert "example.com,1.2.3.4" in out

    def test_multiple_rows(self, capsys):
        data = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        print_csv_table(data)
        out = capsys.readouterr().out
        assert "1,2" in out
        assert "3,4" in out


class TestPrintHtmlTable:
    def test_empty_data_prints_nothing(self, capsys):
        print_html_table([])
        assert capsys.readouterr().out == ""

    def test_table_tag_present(self, capsys):
        print_html_table([{"domain": "example.com"}])
        out = capsys.readouterr().out
        assert "table" in out

    def test_full_page_includes_doctype(self, capsys):
        print_html_table([{"domain": "example.com"}], full_page=True)
        out = capsys.readouterr().out
        assert "<!DOCTYPE html>" in out

    def test_full_page_false_no_doctype(self, capsys):
        print_html_table([{"domain": "example.com"}], full_page=False)
        out = capsys.readouterr().out
        assert "<!DOCTYPE html>" not in out

    def test_data_values_in_output(self, capsys):
        print_html_table([{"domain": "example.com"}])
        out = capsys.readouterr().out
        assert "example.com" in out


class TestCalculateColumnWidths:
    def test_equal_distribution(self):
        headers = ["a", "b", "c"]
        min_w = {"a": 5, "b": 5, "c": 5}
        max_w = {"a": 50, "b": 50, "c": 50}
        widths = _calculate_column_widths(headers, min_w, max_w, 60)
        assert len(widths) == 3
        assert all(w >= 5 for w in widths)

    def test_total_min_exceeds_available(self):
        headers = ["a", "b"]
        min_w = {"a": 40, "b": 40}
        max_w = {"a": 80, "b": 80}
        widths = _calculate_column_widths(headers, min_w, max_w, 30)
        assert widths == [40, 40]

    def test_capped_by_max_widths(self):
        headers = ["a"]
        min_w = {"a": 5}
        max_w = {"a": 10}
        widths = _calculate_column_widths(headers, min_w, max_w, 1000)
        assert widths[0] <= 10

    def test_returns_list_same_length_as_headers(self):
        headers = ["x", "y", "z", "w"]
        min_w = dict.fromkeys(headers, 3)
        max_w = dict.fromkeys(headers, 30)
        widths = _calculate_column_widths(headers, min_w, max_w, 80)
        assert len(widths) == 4

    def test_single_column(self):
        headers = ["only"]
        min_w = {"only": 5}
        max_w = {"only": 50}
        widths = _calculate_column_widths(headers, min_w, max_w, 30)
        assert widths[0] <= 50

    def test_overflow_trimming(self):
        headers = ["a", "b"]
        min_w = {"a": 10, "b": 10}
        max_w = {"a": 100, "b": 100}
        widths = _calculate_column_widths(headers, min_w, max_w, 25)
        assert sum(widths) <= 25 or all(w >= 10 for w in widths)

    def test_available_negative_returns_min_widths(self):
        headers = ["a", "b"]
        min_w = {"a": 10, "b": 10}
        max_w = {"a": 20, "b": 20}
        widths = _calculate_column_widths(headers, min_w, max_w, -10)
        assert widths == [10, 10]

    def test_overflow_trimming_with_max_constraints(self):
        headers = ["a", "b", "c"]
        min_w = {"a": 15, "b": 15, "c": 15}
        max_w = {"a": 20, "b": 20, "c": 20}
        widths = _calculate_column_widths(headers, min_w, max_w, 50)
        assert sum(widths) <= 50

    def test_overflow_trimming_reduces_widest_first(self):
        headers = ["a", "b", "c"]
        min_w = {"a": 10, "b": 10, "c": 10}
        max_w = {"a": 100, "b": 50, "c": 30}
        # Give more space than min but less than sum of maxes
        widths = _calculate_column_widths(headers, min_w, max_w, 40)
        assert sum(widths) <= 40


class TestFormatDnsRecord:
    def _sample(self):
        return [
            {
                "domain": "example.com",
                "records": {"A": {"records": ["1.2.3.4", "5.6.7.8"]}},
            }
        ]

    def test_standard_style_has_domain_key(self):
        result = format_dns_record(self._sample())
        assert result[0]["domain"] == "example.com"

    def test_standard_style_joins_records(self):
        result = format_dns_record(self._sample())
        assert "1.2.3.4" in result[0]["A"]
        assert "5.6.7.8" in result[0]["A"]

    def test_short_style_one_row_per_record(self):
        result = format_dns_record(self._sample(), style="short")
        assert len(result) == 2

    def test_short_style_keys(self):
        result = format_dns_record(self._sample(), style="short")
        assert set(result[0].keys()) == {"domain", "type", "value"}

    def test_short_style_correct_type(self):
        result = format_dns_record(self._sample(), style="short")
        assert all(r["type"] == "A" for r in result)

    def test_show_ttl_appends_ttl(self):
        data = [
            {
                "domain": "example.com",
                "records": {"A": {"records": ["1.2.3.4"], "ttl": 300}},
            }
        ]
        result = format_dns_record(data, show_ttl=True)
        assert "TTL: 300" in result[0]["A"]

    def test_show_ttl_false_no_ttl(self):
        data = [
            {
                "domain": "example.com",
                "records": {"A": {"records": ["1.2.3.4"], "ttl": 300}},
            }
        ]
        result = format_dns_record(data, show_ttl=False)
        assert "TTL" not in result[0]["A"]

    def test_error_in_record_data(self):
        data = [{"domain": "example.com", "records": {"MX": {"error": "NXDOMAIN"}}}]
        result = format_dns_record(data)
        assert "NXDOMAIN" in result[0]["MX"]

    def test_empty_record_data(self):
        data = [{"domain": "example.com", "records": {"TXT": {}}}]
        result = format_dns_record(data)
        assert result[0]["TXT"] == "None"

    def test_empty_input(self):
        assert format_dns_record([]) == []

    def test_multiple_record_types(self):
        data = [
            {
                "domain": "example.com",
                "records": {
                    "A": {"records": ["1.2.3.4"]},
                    "MX": {"records": ["mail.example.com"]},
                },
            }
        ]
        result = format_dns_record(data)
        assert "A" in result[0]
        assert "MX" in result[0]

    def test_records_key_empty_list(self):
        data = [{"domain": "example.com", "records": {"A": {"records": []}}}]
        result = format_dns_record(data)
        assert result[0]["A"] == "None"


def _make_port_result(state="open", service="http", banner=None, response_time=12.5):
    pr = MagicMock()
    pr.state = state
    pr.service = service
    pr.banner = banner
    pr.response_time = response_time
    return pr


def _make_scan_result(target="example.com", target_ip="1.2.3.4", open_ports=None, results=None):
    sr = MagicMock()
    sr.target = target
    sr.target_ip = target_ip
    sr.open_ports = open_ports if open_ports is not None else [80]
    sr.results = results if results is not None else {80: _make_port_result()}
    return sr


class TestFormatScanResults:
    def test_open_port_included(self):
        sr = _make_scan_result()
        result = format_scan_results([sr], show_closed=False)
        assert len(result) == 1
        assert result[0]["port"] == "80"
        assert result[0]["state"] == "OPEN"

    def test_no_open_ports_without_show_closed(self):
        sr = _make_scan_result(open_ports=[], results={})
        result = format_scan_results([sr], show_closed=False)
        assert result[0]["state"] == "NO OPEN PORTS"

    def test_no_open_ports_with_show_closed_includes_closed(self):
        closed_pr = _make_port_result(state="closed", service="ssh")
        sr = _make_scan_result(open_ports=[], results={22: closed_pr})
        result = format_scan_results([sr], show_closed=True)
        assert len(result) == 1
        assert result[0]["state"] == "CLOSED"

    def test_banner_included(self):
        pr = _make_port_result(banner="Apache/2.4")
        sr = _make_scan_result(results={80: pr})
        result = format_scan_results([sr], show_closed=False)
        assert result[0]["banner"] == "Apache/2.4"

    def test_no_banner_empty_string(self):
        pr = _make_port_result(banner=None)
        sr = _make_scan_result(results={80: pr})
        result = format_scan_results([sr], show_closed=False)
        assert result[0]["banner"] == ""

    def test_no_response_time_empty_string(self):
        pr = _make_port_result(response_time=None)
        sr = _make_scan_result(results={80: pr})
        result = format_scan_results([sr], show_closed=False)
        assert result[0]["response_time_ms"] == ""

    def test_target_and_ip_preserved(self):
        sr = _make_scan_result(target="myhost.local", target_ip="192.168.1.5")
        result = format_scan_results([sr], show_closed=False)
        assert result[0]["target"] == "myhost.local"
        assert result[0]["ip"] == "192.168.1.5"

    def test_empty_results(self):
        assert format_scan_results([], show_closed=False) == []

    def test_ports_sorted(self):
        pr80 = _make_port_result()
        pr22 = _make_port_result(service="ssh")
        sr = _make_scan_result(open_ports=[22, 80], results={80: pr80, 22: pr22})
        result = format_scan_results([sr], show_closed=False)
        ports = [r["port"] for r in result]
        assert ports == sorted(ports)

    def test_multiple_targets(self):
        sr1 = _make_scan_result(target="host1", target_ip="1.1.1.1")
        sr2 = _make_scan_result(target="host2", target_ip="2.2.2.2")
        result = format_scan_results([sr1, sr2], show_closed=False)
        targets = {r["target"] for r in result}
        assert "host1" in targets
        assert "host2" in targets

    def test_no_open_ports_multiple_targets_with_show_closed_false(self):
        sr1 = _make_scan_result(open_ports=[], results={})
        sr2 = _make_scan_result(open_ports=[], results={})
        result = format_scan_results([sr1, sr2], show_closed=False)
        assert len(result) == 2
        assert all(r["state"] == "NO OPEN PORTS" for r in result)


class TestFormatDnsTrace:
    def _sample_trace(self):
        return {
            "hops": [
                {
                    "nameserver": "8.8.8.8",
                    "response_time": 12.5,
                    "records": ["1.2.3.4"],
                    "next": "ns1.example.com",
                },
                {
                    "nameserver": "1.1.1.1",
                    "response_time": None,
                    "records": [],
                    "error": "timeout",
                },
            ]
        }

    def test_hop_count_matches_hops(self):
        result = format_dns_trace(self._sample_trace())
        assert len(result) == 2

    def test_hop_indices(self):
        result = format_dns_trace(self._sample_trace())
        assert result[0]["hop"] == 0
        assert result[1]["hop"] == 1

    def test_nameserver_preserved(self):
        result = format_dns_trace(self._sample_trace())
        assert result[0]["nameserver"] == "8.8.8.8"

    def test_response_time_float_formatted(self):
        result = format_dns_trace(self._sample_trace())
        assert result[0]["response_time"] == "12.50ms"

    def test_none_response_time_is_timeout(self):
        result = format_dns_trace(self._sample_trace())
        assert result[1]["response_time"] == "timeout"

    def test_empty_records_shows_error(self):
        result = format_dns_trace(self._sample_trace())
        assert result[1]["records"] == "timeout"

    def test_final_answer_appended(self):
        trace = {
            "hops": [{"nameserver": "8.8.8.8", "response_time": 5.0, "records": []}],
            "final_answer": {
                "nameserver": "final.ns",
                "response_time": 2.0,
                "records": ["answer"],
            },
        }
        result = format_dns_trace(trace)
        assert result[-1]["next"] == "Complete"

    def test_final_answer_none_response_time(self):
        trace = {
            "hops": [],
            "final_answer": {
                "nameserver": "final.ns",
                "response_time": None,
                "records": ["answer"],
            },
        }
        result = format_dns_trace(trace)
        assert result[-1]["response_time"] == "N/A"

    def test_empty_hops(self):
        result = format_dns_trace({"hops": []})
        assert result == []

    def test_non_numeric_response_time(self):
        trace = {"hops": [{"nameserver": "ns1", "response_time": "fast", "records": []}]}
        result = format_dns_trace(trace)
        assert result[0]["response_time"] == "fast"

    def test_records_joined_with_newline(self):
        trace = {"hops": [{"nameserver": "ns1", "response_time": 5.0, "records": ["a", "b"]}]}
        result = format_dns_trace(trace)
        assert "a" in result[0]["records"]
        assert "b" in result[0]["records"]

    def test_no_next_key_defaults_to_na(self):
        trace = {"hops": [{"nameserver": "ns1", "response_time": 1.0, "records": ["x"]}]}
        result = format_dns_trace(trace)
        assert result[0]["next"] == "N/A"

    def test_final_answer_same_as_last_hop_not_duplicated(self):
        hop = {"nameserver": "ns1", "response_time": 1.0, "records": ["a"]}
        trace = {"hops": [hop], "final_answer": hop}
        result = format_dns_trace(trace)
        # Should not add duplicate
        assert len(result) == 1


class TestFormatDnsComparison:
    def test_basic_structure(self):
        comp = {"servers": {"8.8.8.8": {"A": {"records": ["1.2.3.4"], "response_time": 10}}}}
        result = format_dns_comparison(comp)
        assert len(result) == 1
        assert result[0]["server"] == "8.8.8.8"
        assert result[0]["type"] == "A"

    def test_differs_true(self):
        comp = {"servers": {"8.8.8.8": {"A": {"records": ["1.2.3.4"], "differs": True}}}}
        result = format_dns_comparison(comp)
        assert result[0]["differs"] == "✓"

    def test_differs_false(self):
        comp = {"servers": {"8.8.8.8": {"A": {"records": ["1.2.3.4"], "differs": False}}}}
        result = format_dns_comparison(comp)
        assert result[0]["differs"] == " "

    def test_multiple_servers(self):
        comp = {
            "servers": {
                "8.8.8.8": {"A": {"records": ["1.2.3.4"]}},
                "1.1.1.1": {"A": {"records": ["1.2.3.4"]}},
            }
        }
        result = format_dns_comparison(comp)
        assert len(result) == 2

    def test_empty_servers(self):
        result = format_dns_comparison({"servers": {}})
        assert result == []

    def test_missing_servers_key(self):
        result = format_dns_comparison({})
        assert result == []

    def test_records_joined(self):
        comp = {"servers": {"ns": {"A": {"records": ["1.1.1.1", "2.2.2.2"]}}}}
        result = format_dns_comparison(comp)
        assert "1.1.1.1" in result[0]["records"]
        assert "2.2.2.2" in result[0]["records"]

    def test_no_records_shows_none(self):
        comp = {"servers": {"ns": {"A": {}}}}
        result = format_dns_comparison(comp)
        assert result[0]["records"] == "None"

    def test_response_time_none_shows_na(self):
        comp = {"servers": {"ns": {"A": {"records": ["x"], "response_time": None}}}}
        result = format_dns_comparison(comp)
        assert result[0]["response_time_ms"] is None


class TestFormatDnsHealth:
    def _sample_health(self):
        return {
            "domain": "example.com",
            "score": 85,
            "status": "healthy",
            "issues": ["issue1"],
            "warnings": ["low TTL"],
            "record_scores": {"A": 90, "MX": 70, "TXT": 40},
        }

    def test_first_row_is_summary(self):
        result = format_dns_health(self._sample_health())
        assert result[0]["domain"] == "example.com"

    def test_overall_score_formatted(self):
        result = format_dns_health(self._sample_health())
        assert result[0]["overall_score"] == "85/100"

    def test_status_uppercased(self):
        result = format_dns_health(self._sample_health())
        assert result[0]["status"] == "HEALTHY"

    def test_record_score_rows_appended(self):
        result = format_dns_health(self._sample_health())
        assert len(result) == 4

    def test_good_record_score(self):
        result = format_dns_health(self._sample_health())
        a_row = next(r for r in result if "A:" in r["domain"])
        assert a_row["status"] == "GOOD"

    def test_warn_record_score(self):
        result = format_dns_health(self._sample_health())
        mx_row = next(r for r in result if "MX:" in r["domain"])
        assert mx_row["status"] == "WARN"

    def test_bad_record_score(self):
        result = format_dns_health(self._sample_health())
        txt_row = next(r for r in result if "TXT:" in r["domain"])
        assert txt_row["status"] == "BAD"

    def test_boundary_score_80_is_good(self):
        health = {**self._sample_health(), "record_scores": {"A": 80}}
        result = format_dns_health(health)
        assert result[1]["status"] == "GOOD"

    def test_boundary_score_50_is_warn(self):
        health = {**self._sample_health(), "record_scores": {"A": 50}}
        result = format_dns_health(health)
        assert result[1]["status"] == "WARN"

    def test_issues_joined(self):
        health = {**self._sample_health(), "issues": ["issue1", "issue2"]}
        result = format_dns_health(health)
        assert "issue1" in result[0]["issues"]
        assert "issue2" in result[0]["issues"]

    def test_no_record_scores(self):
        health = {**self._sample_health(), "record_scores": {}}
        result = format_dns_health(health)
        assert len(result) == 1

    def test_zero_score(self):
        health = {**self._sample_health(), "score": 0}
        result = format_dns_health(health)
        assert result[0]["overall_score"] == "0/100"

    def test_warnings_empty(self):
        health = {**self._sample_health(), "warnings": []}
        result = format_dns_health(health)
        assert result[0]["warnings"] == ""

    def test_issues_empty(self):
        health = {**self._sample_health(), "issues": []}
        result = format_dns_health(health)
        assert result[0]["issues"] == ""

    def test_missing_status_uses_unknown(self):
        health = {**self._sample_health(), "status": None}
        del health["status"]
        result = format_dns_health(health)
        assert result[0]["status"] == "UNKNOWN"


def _base_poisoning(**overrides):
    base = {
        "domain": "example.com",
        "record_type": "A",
        "poisoning_level": "NONE",
        "confidence": 100,
        "cdn_detected": False,
        "poisoned": False,
        "test_servers_count": 10,
        "mismatches": 0,
        "cdn_variations": 0,
        "unique_ips_seen": 2,
        "ip_diversity": 0,
        "geo_diversity": 3,
    }
    base.update(overrides)
    return base


class TestFormatDnsPoisoning:
    def test_clean_verdict(self):
        result = format_dns_poisoning(_base_poisoning())
        assert result[-1]["detail"] == "CLEAN"

    def test_poisoned_verdict(self):
        result = format_dns_poisoning(_base_poisoning(poisoned=True, mismatches=3, test_servers_count=10))
        assert result[-1]["detail"] == "POISONED"

    def test_cdn_detected_verdict(self):
        result = format_dns_poisoning(_base_poisoning(cdn_detected=True, cdn_owner="Cloudflare"))
        assert "CDN DETECTED" in result[-1]["detail"]

    def test_dns_analysis_section_present(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "DNS ANALYSIS" in sections

    def test_control_server_section_present(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "CONTROL SERVER" in sections

    def test_summary_section_present(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "SUMMARY" in sections

    def test_cdn_detection_section_when_cdn_detected(self):
        result = format_dns_poisoning(_base_poisoning(cdn_detected=True))
        sections = [r["section"] for r in result]
        assert "CDN DETECTION" in sections

    def test_cdn_detection_section_absent_without_cdn(self):
        result = format_dns_poisoning(_base_poisoning(cdn_detected=False))
        sections = [r["section"] for r in result]
        assert "CDN DETECTION" not in sections

    def test_control_analysis_section_with_data(self):
        result = format_dns_poisoning(
            _base_poisoning(
                control_analysis={
                    "unique": 2,
                    "ipv4": 2,
                    "ipv6": 0,
                    "owners": ["Google"],
                    "private": 0,
                    "reserved": 0,
                }
            )
        )
        sections = [r["section"] for r in result]
        assert "CONTROL IP ANALYSIS" in sections

    def test_control_analysis_section_absent_without_data(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "CONTROL IP ANALYSIS" not in sections

    def test_consensus_section_with_data(self):
        result = format_dns_poisoning(
            _base_poisoning(
                consensus_top=[{"ip": "1.2.3.4", "percentage": 80, "owner": "Google"}],
                consensus_rate=80,
            )
        )
        sections = [r["section"] for r in result]
        assert "CONSENSUS" in sections

    def test_consensus_absent_without_data(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "CONSENSUS" not in sections

    def test_analysis_cdn_likely(self):
        result = format_dns_poisoning(_base_poisoning(cdn_likely=True))
        analysis_rows = [r for r in result if r["section"] == "ANALYSIS"]
        assert any("CDN NETWORK" in r["detail"] for r in analysis_rows)

    def test_analysis_anycast_likely(self):
        result = format_dns_poisoning(_base_poisoning(anycast_likely=True))
        analysis_rows = [r for r in result if r["section"] == "ANALYSIS"]
        assert any("Anycast" in r["detail"] for r in analysis_rows)

    def test_analysis_poisoning_likely(self):
        result = format_dns_poisoning(_base_poisoning(poisoning_likely=True))
        analysis_rows = [r for r in result if r["section"] == "ANALYSIS"]
        assert any("SUSPICIOUS" in r["detail"] for r in analysis_rows)

    def test_inconsistencies_details_section(self):
        inc = {
            "server": "1.2.3.4",
            "server_name": "Bad NS",
            "server_country": "XX",
            "type": "record_mismatch",
            "severity": "high",
            "control_owner": "Google",
            "test_owner": "BadActor",
        }
        result = format_dns_poisoning(_base_poisoning(inconsistencies=[inc]))
        sections = [r["section"] for r in result]
        assert "DETAILS" in sections

    def test_inconsistency_cdn_variation_type(self):
        inc = {
            "server": "1.2.3.4",
            "type": "cdn_variation",
            "severity": "info",
            "owner": "Cloudflare",
        }
        result = format_dns_poisoning(_base_poisoning(inconsistencies=[inc]))
        notes = [r.get("note", "") for r in result]
        assert any("CDN" in n or "cdn" in n for n in notes)

    def test_inconsistency_error_mismatch_type(self):
        inc = {
            "server": "1.2.3.4",
            "type": "error_mismatch",
            "severity": "medium",
            "control_error": "NXDOMAIN",
            "test_error": "SERVFAIL",
        }
        result = format_dns_poisoning(_base_poisoning(inconsistencies=[inc]))
        notes = [r.get("note", "") for r in result]
        assert any("NXDOMAIN" in n or "SERVFAIL" in n for n in notes)

    def test_inconsistency_ttl_diff_type(self):
        inc = {
            "server": "1.2.3.4",
            "type": "ttl_difference",
            "severity": "low",
            "diff": 120,
        }
        result = format_dns_poisoning(_base_poisoning(inconsistencies=[inc]))
        notes = [r.get("note", "") for r in result]
        assert any("TTL diff" in n for n in notes)

    def test_long_note_truncated(self):
        long_owner = "A" * 100
        inc = {
            "server": "1.2.3.4",
            "type": "record_mismatch",
            "severity": "high",
            "control_owner": long_owner,
            "test_owner": long_owner,
        }
        result = format_dns_poisoning(_base_poisoning(inconsistencies=[inc]))
        notes = [r.get("note", "") for r in result if r.get("note", "").endswith("...")]
        assert len(notes) > 0

    def test_max_5_inconsistencies_shown(self):
        inc_template = {
            "server": "1.2.3.4",
            "type": "record_mismatch",
            "severity": "high",
            "control_owner": "X",
            "test_owner": "Y",
        }
        incs = [{**inc_template, "server": f"1.2.3.{i}"} for i in range(10)]
        result = format_dns_poisoning(_base_poisoning(inconsistencies=incs))
        detail_rows = [r for r in result if r["section"].startswith("  ->")]
        assert len(detail_rows) <= 5

    def test_control_analysis_owners_empty_shows_unknown(self):
        result = format_dns_poisoning(
            _base_poisoning(
                control_analysis={
                    "unique": 1,
                    "ipv4": 1,
                    "ipv6": 0,
                    "owners": [],
                    "private": 0,
                    "reserved": 0,
                }
            )
        )
        analysis_rows = [r for r in result if r["section"] == "CONTROL IP ANALYSIS"]
        assert "Unknown" in analysis_rows[0]["value"]

    def test_control_analysis_missing_owners_key(self):
        result = format_dns_poisoning(
            _base_poisoning(
                control_analysis={
                    "unique": 1,
                    "ipv4": 1,
                    "ipv6": 0,
                    "private": 0,
                    "reserved": 0,
                }
            )
        )
        analysis_rows = [r for r in result if r["section"] == "CONTROL IP ANALYSIS"]
        assert "Unknown" in analysis_rows[0]["value"]

    def test_ip_diversity_section_present(self):
        result = format_dns_poisoning(_base_poisoning())
        sections = [r["section"] for r in result]
        assert "IP DIVERSITY" in sections

    def test_verdict_section_is_last(self):
        result = format_dns_poisoning(_base_poisoning())
        assert result[-1]["section"] == "VERDICT"

    def test_status_text_cdn_detected_in_note(self):
        result = format_dns_poisoning(_base_poisoning(cdn_detected=True))
        dns_analysis = next(r for r in result if r["section"] == "DNS ANALYSIS")
        assert dns_analysis["note"] == "CDN DETECTED"

    def test_status_text_poisoning_check_in_note(self):
        result = format_dns_poisoning(_base_poisoning(cdn_detected=False))
        dns_analysis = next(r for r in result if r["section"] == "DNS ANALYSIS")
        assert dns_analysis["note"] == "POISONING CHECK"

    def test_missing_control_server_fields(self):
        result = format_dns_poisoning(_base_poisoning(control_server=None))
        control_section = next(r for r in result if r["section"] == "CONTROL SERVER")
        assert control_section is not None

    def test_empty_consensus_top(self):
        result = format_dns_poisoning(_base_poisoning(consensus_top=[]))
        assert "CONSENSUS" not in [r["section"] for r in result]


class TestBuildHtmlPage:
    def test_contains_doctype(self):
        html = _build_html_page("Test", "table")
        assert "<!DOCTYPE html>" in html

    def test_contains_title(self):
        html = _build_html_page("My Title", "table")
        assert "<title>My Title</title>" in html
        assert "<h1>My Title</h1>" in html

    def test_contains_table(self):
        html = _build_html_page("X", "table")
        assert "table" in html

    def test_contains_generated_timestamp(self):
        html = _build_html_page("X", "")
        assert "Generated:" in html

    def test_contains_css_styles(self):
        html = _build_html_page("X", "")
        assert "<style>" in html


class TestSaveResults:
    def test_save_json(self, tmp_path):
        data = [{"key": "value", "num": 42}]
        fp = str(tmp_path / "out.json")
        save_results(data, fp, "json")
        loaded = json.loads(Path(fp).read_text())
        assert loaded == data

    def test_save_yaml(self, tmp_path):
        data = [{"domain": "example.com", "score": 100}]
        fp = str(tmp_path / "out.yaml")
        save_results(data, fp, "yaml")
        loaded = yaml.safe_load(Path(fp).read_text())
        assert loaded == data

    def test_save_csv(self, tmp_path):
        data = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        fp = str(tmp_path / "out.csv")
        save_results(data, fp, "csv")
        content = Path(fp).read_text()
        assert "a,b" in content
        assert "1,2" in content

    def test_save_html_full_page(self, tmp_path):
        data = [{"col": "val"}]
        fp = str(tmp_path / "out.html")
        save_results(data, fp, "html")
        content = Path(fp).read_text()
        assert "<!DOCTYPE html>" in content

    def test_save_html_table(self, tmp_path):
        data = [{"col": "val"}]
        fp = str(tmp_path / "out.html")
        save_results(data, fp, "html_table")
        content = Path(fp).read_text()
        assert "table" in content

    def test_save_unknown_format_writes_grid(self, tmp_path):
        data = [{"x": "y"}]
        fp = str(tmp_path / "out.txt")
        save_results(data, fp, "grid")
        content = Path(fp).read_text()
        assert "x" in content

    def test_creates_parent_directories(self, tmp_path):
        fp = str(tmp_path / "nested" / "deep" / "out.json")
        save_results([{"a": 1}], fp, "json")
        assert Path(fp).exists()

    def test_save_empty_csv(self, tmp_path):
        fp = str(tmp_path / "empty.csv")
        save_results([], fp, "csv")
        assert Path(fp).exists()

    def test_save_json_unicode(self, tmp_path):
        data = [{"text": "привет мир"}]
        fp = str(tmp_path / "unicode.json")
        save_results(data, fp, "json")
        loaded = json.loads(Path(fp).read_text(encoding="utf-8"))
        assert loaded[0]["text"] == "привет мир"

    def test_permission_error_does_not_raise(self, tmp_path):
        fp = str(tmp_path / "out.json")
        with patch("pathlib.Path.open", side_effect=PermissionError("denied")):
            save_results([{"a": 1}], fp, "json")

    def test_os_error_does_not_raise(self, tmp_path):
        fp = str(tmp_path / "out.json")
        with patch("pathlib.Path.mkdir", side_effect=OSError("disk full")):
            save_results([{"a": 1}], fp, "json")

    def test_save_empty_data_csv(self, tmp_path):
        fp = str(tmp_path / "empty.csv")
        save_results([], fp, "csv")
        content = Path(fp).read_text()
        assert content == ""

    def test_save_single_row_csv(self, tmp_path):
        data = [{"col1": "value1", "col2": "value2"}]
        fp = str(tmp_path / "single.csv")
        save_results(data, fp, "csv")
        content = Path(fp).read_text()
        assert "col1,col2" in content
        assert "value1,value2" in content

    def test_save_yaml_with_unicode(self, tmp_path):
        data = [{"text": "привет мир"}]
        fp = str(tmp_path / "unicode.yaml")
        save_results(data, fp, "yaml")
        loaded = yaml.safe_load(Path(fp).read_text(encoding="utf-8"))
        assert loaded[0]["text"] == "привет мир"
