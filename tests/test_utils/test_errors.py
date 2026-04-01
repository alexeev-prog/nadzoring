"""Tests for nadzoring.utils.errors."""

import pytest

from nadzoring.utils.errors import (
    ARPCacheRetrievalError,
    ARPError,
    ConnectionTimeoutError,
    DNSDomainNotFoundError,
    DNSError,
    DNSNoRecordsError,
    DNSResolutionError,
    DNSTimeoutError,
    HostResolutionError,
    InvalidDomainError,
    InvalidIPAddressError,
    InvalidPortError,
    NadzoringError,
    NetworkError,
    UnsupportedPlatformError,
    ValidationError,
)


class TestExceptionHierarchy:
    def test_nadzoring_error_is_exception(self):
        assert issubclass(NadzoringError, Exception)

    def test_dns_error_is_nadzoring_error(self):
        assert issubclass(DNSError, NadzoringError)

    def test_network_error_is_nadzoring_error(self):
        assert issubclass(NetworkError, NadzoringError)

    def test_arp_error_is_nadzoring_error(self):
        assert issubclass(ARPError, NadzoringError)

    def test_validation_error_is_nadzoring_error(self):
        assert issubclass(ValidationError, NadzoringError)

    def test_dns_resolution_error_is_dns_error(self):
        assert issubclass(DNSResolutionError, DNSError)

    def test_dns_timeout_error_is_dns_error(self):
        assert issubclass(DNSTimeoutError, DNSError)

    def test_dns_domain_not_found_is_dns_error(self):
        assert issubclass(DNSDomainNotFoundError, DNSError)

    def test_dns_no_records_is_dns_error(self):
        assert issubclass(DNSNoRecordsError, DNSError)

    def test_host_resolution_error_is_network_error(self):
        assert issubclass(HostResolutionError, NetworkError)

    def test_connection_timeout_is_network_error(self):
        assert issubclass(ConnectionTimeoutError, NetworkError)

    def test_unsupported_platform_is_network_error(self):
        assert issubclass(UnsupportedPlatformError, NetworkError)

    def test_arp_cache_retrieval_is_arp_error(self):
        assert issubclass(ARPCacheRetrievalError, ARPError)

    def test_invalid_ip_is_validation_error(self):
        assert issubclass(InvalidIPAddressError, ValidationError)

    def test_invalid_domain_is_validation_error(self):
        assert issubclass(InvalidDomainError, ValidationError)

    def test_invalid_port_is_validation_error(self):
        assert issubclass(InvalidPortError, ValidationError)


class TestExceptionRaising:
    def test_raise_nadzoring_error(self):
        with pytest.raises(NadzoringError):
            raise NadzoringError("base error")

    def test_raise_dns_resolution_error(self):
        with pytest.raises(DNSResolutionError):
            raise DNSResolutionError("cannot resolve")

    def test_dns_resolution_caught_as_dns_error(self):
        with pytest.raises(DNSError):
            raise DNSResolutionError("cannot resolve")

    def test_dns_resolution_caught_as_nadzoring_error(self):
        with pytest.raises(NadzoringError):
            raise DNSResolutionError("cannot resolve")

    def test_raise_dns_timeout(self):
        with pytest.raises(DNSTimeoutError):
            raise DNSTimeoutError("timed out")

    def test_raise_dns_domain_not_found(self):
        with pytest.raises(DNSDomainNotFoundError):
            raise DNSDomainNotFoundError("NXDOMAIN")

    def test_raise_dns_no_records(self):
        with pytest.raises(DNSNoRecordsError):
            raise DNSNoRecordsError("no A records")

    def test_raise_host_resolution_error(self):
        with pytest.raises(HostResolutionError):
            raise HostResolutionError("cannot resolve host")

    def test_host_resolution_caught_as_network_error(self):
        with pytest.raises(NetworkError):
            raise HostResolutionError("cannot resolve host")

    def test_raise_connection_timeout(self):
        with pytest.raises(ConnectionTimeoutError):
            raise ConnectionTimeoutError("connection timed out")

    def test_raise_unsupported_platform(self):
        with pytest.raises(UnsupportedPlatformError):
            raise UnsupportedPlatformError("OS not supported")

    def test_raise_arp_cache_retrieval(self):
        with pytest.raises(ARPCacheRetrievalError):
            raise ARPCacheRetrievalError("failed to read ARP cache")

    def test_arp_cache_retrieval_caught_as_arp_error(self):
        with pytest.raises(ARPError):
            raise ARPCacheRetrievalError("failed to read ARP cache")

    def test_raise_invalid_ip(self):
        with pytest.raises(InvalidIPAddressError):
            raise InvalidIPAddressError("not-an-ip")

    def test_invalid_ip_caught_as_validation_error(self):
        with pytest.raises(ValidationError):
            raise InvalidIPAddressError("not-an-ip")

    def test_raise_invalid_domain(self):
        with pytest.raises(InvalidDomainError):
            raise InvalidDomainError("-bad.com")

    def test_raise_invalid_port(self):
        with pytest.raises(InvalidPortError):
            raise InvalidPortError("0")

    def test_exception_message_preserved(self):
        msg = "specific error message"
        exc = DNSResolutionError(msg)
        assert str(exc) == msg

    def test_exception_args_preserved(self):
        exc = InvalidPortError("port", 99999)
        assert exc.args == ("port", 99999)

    def test_all_leaf_errors_catchable_as_base(self):
        leaf_errors = [
            DNSResolutionError,
            DNSTimeoutError,
            DNSDomainNotFoundError,
            DNSNoRecordsError,
            HostResolutionError,
            ConnectionTimeoutError,
            UnsupportedPlatformError,
            ARPCacheRetrievalError,
            InvalidIPAddressError,
            InvalidDomainError,
            InvalidPortError,
        ]
        for error_cls in leaf_errors:
            with pytest.raises(NadzoringError):
                raise error_cls("test")
