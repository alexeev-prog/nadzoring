"""Literal error types for network base operations.

This module defines closed sets of possible error strings returned by
network-related functions (ping, traceroute, WHOIS, port scanning, etc.).

All network functions that return a dictionary with an ``"error"`` field
or raise exceptions with specific messages should use these types.

Example:
    from nadzoring.network_base.whois_lookup import whois_lookup
    from nadzoring.network_base.errors import WHOISError

    result = whois_lookup("example.com")
    if result.get("error") == "Command not found":
        install_whois()
"""

from typing import Literal

PingError = Literal[
    "Host unreachable",
    "Timeout",
    "Permission denied (needs root)",
    "Invalid address",
]
"""Possible error strings for ICMP ping operations.

Values:
    - ``"Host unreachable"``: The target host did not respond to ICMP
      echo requests.
    - ``"Timeout"``: The ping request exceeded the timeout period.
    - ``"Permission denied (needs root)"``: Raw socket creation requires
      elevated privileges on some systems.
    - ``"Invalid address"``: The provided address could not be resolved
      or is malformed.
"""

TracerouteError = Literal[
    "Permission denied (needs root)",
    "Command not found",
    "Network unreachable",
    "DNS resolution failed",
    "Timeout",
]
"""Possible error strings for traceroute operations.

Values:
    - ``"Permission denied (needs root)"``: Traceroute requires raw socket
      privileges on Linux.
    - ``"Command not found"``: The traceroute command is not installed.
    - ``"Network unreachable"``: The target network is unreachable.
    - ``"DNS resolution failed"``: Could not resolve the target hostname.
    - ``"Timeout"``: The traceroute operation exceeded the overall timeout.
"""

WHOISError = Literal[
    "Command not found",
    "Query timeout",
    "No information found",
    "Invalid target",
]
"""Possible error strings for WHOIS lookup operations.

Values:
    - ``"Command not found"``: The whois command is not installed.
    - ``"Query timeout"``: The WHOIS query exceeded the timeout period.
    - ``"No information found"``: The WHOIS server returned no information
      for the target.
    - ``"Invalid target"``: The provided domain or IP address is invalid.
"""

PortScanError = Literal[
    "Connection refused",
    "Timeout",
    "Host unreachable",
    "Invalid port range",
    "Resolution failed",
]
"""Possible error strings for port scanning operations.

Values:
    - ``"Connection refused"``: The target host actively refused the
      connection on the specified port.
    - ``"Timeout"``: The connection attempt exceeded the timeout period.
    - ``"Host unreachable"``: The target host is not reachable on the network.
    - ``"Invalid port range"``: The specified port range is invalid
      (e.g., start > end, out of 1-65535 range).
    - ``"Resolution failed"``: Could not resolve the target hostname to
      an IP address.
"""

GeolocationError = Literal[
    "API request failed",
    "Rate limit exceeded",
    "Invalid IP address",
    "Private IP address",
]
"""Possible error strings for IP geolocation operations.

Values:
    - ``"API request failed"``: The geolocation API request failed due to
      network error or server error.
    - ``"Rate limit exceeded"``: The free API rate limit has been exceeded.
    - ``"Invalid IP address"``: The provided string is not a valid IP address.
    - ``"Private IP address"``: The IP address is in a private range and
      cannot be geolocated.
"""
