"""
Centralized exception hierarchy for Nadzoring.

All public exceptions are defined here so that consumers can import
from a single location and catch errors at the appropriate granularity.
"""


class NadzoringError(Exception):
    """Base exception for all Nadzoring errors."""


# ---------------------------------------------------------------------------
# DNS errors
# ---------------------------------------------------------------------------


class DNSError(NadzoringError):
    """Base exception for DNS-related failures."""


class DNSResolutionError(DNSError):
    """Raised when a DNS query cannot be resolved."""


class DNSTimeoutError(DNSError):
    """Raised when a DNS query times out."""


class DNSDomainNotFoundError(DNSError):
    """Raised when the queried domain does not exist (NXDOMAIN)."""


class DNSNoRecordsError(DNSError):
    """Raised when a domain exists but has no records of the requested type."""


# ---------------------------------------------------------------------------
# Network errors
# ---------------------------------------------------------------------------


class NetworkError(NadzoringError):
    """Base exception for network-related failures."""


class HostResolutionError(NetworkError):
    """Raised when a hostname cannot be resolved to an IP address."""


class ConnectionTimeoutError(NetworkError):
    """Raised when a network connection attempt times out."""


class UnsupportedPlatformError(NetworkError):
    """Raised when the current OS is not supported by a function."""


# ---------------------------------------------------------------------------
# ARP errors
# ---------------------------------------------------------------------------


class ARPError(NadzoringError):
    """Base exception for ARP-related failures."""


class ARPCacheRetrievalError(ARPError):
    """Raised when reading the ARP cache fails."""


# ---------------------------------------------------------------------------
# Input validation errors
# ---------------------------------------------------------------------------


class ValidationError(NadzoringError):
    """Raised when user-supplied input fails validation."""


class InvalidIPAddressError(ValidationError):
    """Raised when a string is not a valid IP address."""


class InvalidDomainError(ValidationError):
    """Raised when a string is not a valid domain name."""


class InvalidPortError(ValidationError):
    """Raised when a port number is outside the valid 1-65535 range."""
