"""Literal error types for ARP-related operations.

This module defines error strings for ARP cache retrieval and spoofing
detection operations. Functions that raise exceptions with specific
error messages use these literals as the exception message strings.

Example:
    from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
    from nadzoring.arp.errors import ARPCacheError

    try:
        cache = ARPCache()
        entries = cache.get_cache()
    except ARPCacheRetrievalError as e:
        if str(e) == "Command not found":
            install_missing_tool()
"""

from typing import Literal

ARPCacheError = Literal[
    "Command not found",
    "Permission denied (needs root)",
    "Unsupported platform",
    "Failed to parse ARP cache output",
]
"""Possible error strings for ARP cache retrieval operations.

Values:
    - ``"Command not found"``: The required system command (ip, arp) is
      not installed or not in PATH.
    - ``"Permission denied (needs root)"``: The command requires elevated
      privileges to read the ARP cache.
    - ``"Unsupported platform"``: The current operating system is not
      supported (not Linux, Windows, or macOS).
    - ``"Failed to parse ARP cache output"``: The command succeeded but
      its output could not be parsed into ARP entries.
"""

ARPSpoofingError = Literal[
    "No network interface specified",
    "Packet capture failed",
    "No ARP packets captured",
]
"""Possible error strings for ARP spoofing detection operations.

Values:
    - ``"No network interface specified"``: A network interface was not
      provided and could not be auto-detected.
    - ``"Packet capture failed"``: The packet capture (sniffing) operation
      failed due to permissions or network issues.
    - ``"No ARP packets captured"``: The capture completed but no ARP
      packets were observed.
"""
