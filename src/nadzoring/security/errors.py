"""Literal error types for security-related operations.

This module defines closed sets of possible error strings returned by
security-related functions (SSL/TLS, HTTP headers, email security, etc.).

All security functions that return a dictionary with an ``"error"`` field
should use these types to annotate that field.

Example:
    from nadzoring.security.check_website_ssl_cert import check_ssl_certificate
    from nadzoring.security.errors import SSLCertError

    result = check_ssl_certificate("example.com")
    if result["error"] == "Certificate expired":
        handle_expired_cert()
    elif result["error"] == "Hostname mismatch":
        handle_mismatch()
"""

from typing import Literal

SSLCertError = Literal[
    "Certificate expired",
    "Certificate not yet valid",
    "Hostname mismatch",
    "Self-signed certificate",
    "Connection timeout",
    "SSL handshake failed",
    "Certificate verification failed",
    "No certificate returned",
]
"""Possible error strings for SSL/TLS certificate operations.

Values:
    - ``"Certificate expired"``: The certificate's expiry date has passed.
    - ``"Certificate not yet valid"``: The certificate's not-before date
      is in the future.
    - ``"Hostname mismatch"``: The certificate does not match the requested
      domain name.
    - ``"Self-signed certificate"``: The certificate is self-signed and
      cannot be verified against a trusted CA.
    - ``"Connection timeout"``: Could not establish a connection to the
      server within the timeout period.
    - ``"SSL handshake failed"``: The TLS handshake failed due to protocol
      mismatch, cipher mismatch, or other TLS-level error.
    - ``"Certificate verification failed"``: The certificate chain could
      not be verified against the system's CA bundle.
    - ``"No certificate returned"``: The server did not provide a certificate
      during the TLS handshake.
"""

HTTPHeaderError = Literal[
    "Request timeout",
    "Connection refused",
    "SSL verification failed",
    "Too many redirects",
    "Invalid URL",
]
"""Possible error strings for HTTP security header checks.

Values:
    - ``"Request timeout"``: The HTTP request exceeded the configured
      timeout.
    - ``"Connection refused"``: The server actively refused the connection.
    - ``"SSL verification failed"``: SSL certificate verification failed
      while verify_ssl=True.
    - ``"Too many redirects"``: The request exceeded the maximum redirect
      limit.
    - ``"Invalid URL"``: The provided URL string could not be parsed.
"""

EmailSecurityError = Literal[
    "No SPF record",
    "No DKIM record",
    "No DMARC record",
    "SPF lookup timeout",
    "DKIM lookup timeout",
    "DMARC lookup timeout",
]
"""Possible error strings for email security (SPF/DKIM/DMARC) checks.

Values:
    - ``"No SPF record"``: No SPF TXT record was found for the domain.
    - ``"No DKIM record"``: No DKIM records were found for common selectors.
    - ``"No DMARC record"``: No DMARC TXT record was found at _dmarc.domain.
    - ``"SPF lookup timeout"``: DNS query for SPF record timed out.
    - ``"DKIM lookup timeout"``: DNS query for DKIM record timed out.
    - ``"DMARC lookup timeout"``: DNS query for DMARC record timed out.
"""

SubdomainError = Literal[
    "CT log query failed",
    "Wordlist file not found",
    "DNS resolution failed",
]
"""Possible error strings for subdomain discovery operations.

Values:
    - ``"CT log query failed"``: The certificate transparency log query
      returned an error or could not be parsed.
    - ``"Wordlist file not found"``: The specified wordlist file does
      not exist or cannot be read.
    - ``"DNS resolution failed"``: Could not resolve subdomain candidates
      due to resolver issues.
"""
