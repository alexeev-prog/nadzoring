"""Literal error types for DNS lookup operations.

This module defines closed sets of possible error strings returned by
DNS-related functions. Using Literal types instead of plain strings enables
static type checking, IDE autocompletion, and guarantees that error values
are documented in a single source of truth.

All DNS functions that return a dictionary with an ``"error"`` field should
use these types to annotate that field. Consumers can then pattern-match
on specific error strings with confidence that typos will be caught by
type checkers.

Example:
    from nadzoring.dns_lookup.utils import resolve_with_timer
    from nadzoring.dns_lookup.errors import DNSResolveError

    result = resolve_with_timer("example.com", "A")
    error = result.get("error")
    if error == "Domain does not exist":
        handle_nxdomain()
    elif error == "Query timeout":
        retry_with_longer_timeout()
"""

from typing import Literal

DNSResolveError = Literal[
    "Domain does not exist",
    "No records of requested type",
    "Query timeout",
    "Operation exceeded lifetime timeout",
    "Resolver error",
]
"""Possible error strings for forward DNS resolution operations.

Values:
    - ``"Domain does not exist"``: NXDOMAIN response from the nameserver.
    - ``"No records of requested type"``: Domain exists but has no records
      of the queried type (e.g., A, MX, TXT).
    - ``"Query timeout"``: Nameserver did not respond within the configured
      read timeout.
    - ``"Operation exceeded lifetime timeout"``: The entire operation
      exceeded the configured lifetime timeout.
    - ``"Resolver error"``: Unexpected error from the underlying DNS
      resolver library.
"""

DNSReverseError = Literal[
    "No PTR record",
    "No reverse DNS",
    "Query timeout",
    "Invalid IP address",
    "Resolver error",
]
"""Possible error strings for reverse DNS (PTR) lookups.

Values:
    - ``"No PTR record"``: IP address exists but has no PTR record.
    - ``"No reverse DNS"``: NXDOMAIN on the reverse lookup zone.
    - ``"Query timeout"``: Nameserver did not respond within the timeout.
    - ``"Invalid IP address"``: The provided string is not a valid IPv4
      or IPv6 address.
    - ``"Resolver error"``: Unexpected error from the resolver.
"""

DNSTraceError = Literal[
    "Loop detected",
    "Delegation error",
    "No further delegation",
    "Timeout",
    "Domain does not exist",
    "No answer",
]
"""Possible error strings for DNS trace operations.

Values:
    - ``"Loop detected"``: The delegation chain contained a cycle.
    - ``"Delegation error"``: Failed to resolve the next nameserver
      during delegation.
    - ``"No further delegation"``: Reached a nameserver that does not
      provide further delegation information.
    - ``"Timeout"``: A query in the delegation chain timed out.
    - ``"Domain does not exist"``: NXDOMAIN response during trace.
    - ``"No answer"``: Nameserver responded but provided no answer.
"""

DNSComparisonError = Literal[
    "No baseline server",
    "Query failed for baseline",
    "Record type mismatch",
]
"""Possible error strings for DNS comparison operations.

Values:
    - ``"No baseline server"``: The servers list was empty.
    - ``"Query failed for baseline"``: Could not obtain results from the
      baseline (first) server.
    - ``"Record type mismatch"``: Servers returned records of different
      types for the same query.
"""

DNSHealthError = Literal[
    "No nameservers configured",
    "All record types failed",
    "Health check timeout",
]
"""Possible error strings for DNS health check operations.

Values:
    - ``"No nameservers configured"``: No nameservers were provided for
      the health check.
    - ``"All record types failed"``: Every queried record type returned
      an error.
    - ``"Health check timeout"``: The health check exceeded the lifetime
      timeout.
"""
