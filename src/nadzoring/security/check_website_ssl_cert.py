import socket
import ssl
from datetime import UTC, datetime
from ssl import SSLContext

import certifi


def check_ssl_expiry(
    domain: str, *, days_before: int = 7
) -> dict[str, int | datetime | str]:
    """
    Check SSL certificate expiry for a given domain.

    Args:
        domain: The domain name to check SSL certificate for
        days_before: Number of days before expiry to consider as warning threshold

    Returns:
        A dictionary containing domain information, remaining days until expiry,
        and the warning threshold days.

    Raises:
        ssl.SSLCertVerificationError: If SSL certificate verification fails
        socket.gaierror: If domain cannot be resolved
        ConnectionRefusedError: If connection to port 443 is refused
        KeyError: If certificate doesn't contain 'notAfter' field

    """
    context: SSLContext = ssl.create_default_context()

    context.load_verify_locations(certifi.where())

    with (
        socket.create_connection((domain, 443), timeout=10) as sock,
        context.wrap_socket(sock, server_hostname=domain) as ssock,
    ):
        cert: (
            dict[
                str,
                str
                | tuple[tuple[str, str], ...]
                | tuple[tuple[tuple[str, str], ...], ...],
            ]
            | None
        ) = ssock.getpeercert()

    expiry_date: datetime = datetime.strptime(
        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=UTC)

    remaining_days: int = (expiry_date - datetime.now(UTC)).days

    return {
        "domain": domain,
        "remaining days": remaining_days,
        "days before": days_before,
    }


def check_ssl_expiry_with_fallback(
    domain: str, days_before: int = 7
) -> dict[str, int | datetime | str]:
    """
    Check SSL certificate expiry with fallback options if verification fails.

    Tries multiple SSL context configurations to handle different systems
    and certificate chain issues.

    Args:
        domain: The domain name to check SSL certificate for
        days_before: Number of days before expiry to consider as warning threshold

    Returns:
        A dictionary containing domain information, remaining days until expiry,
        and the warning threshold days.

    """
    errors: list[str] = []

    try:
        return check_ssl_expiry(domain, days_before)
    except ssl.SSLCertVerificationError as e:
        errors.append(f"Default SSL context: {e}")

    try:
        context: SSLContext = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with (
            socket.create_connection((domain, 443), timeout=10) as sock,
            context.wrap_socket(sock, server_hostname=domain) as ssock,
        ):
            cert: (
                dict[
                    str,
                    str
                    | tuple[tuple[str, str], ...]
                    | tuple[tuple[tuple[str, str], ...], ...],
                ]
                | None
            ) = ssock.getpeercert()

        expiry_date: datetime = datetime.strptime(
            cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
        ).replace(tzinfo=UTC)

        remaining_days: int = (expiry_date - datetime.now(UTC)).days
    except Exception as e:
        errors.append(f"No verification context: {e}")
    else:
        return {
            "domain": domain,
            "remaining days": remaining_days,
            "days before": days_before,
            "warning": "Certificate verification disabled",
        }

    raise ssl.SSLCertVerificationError(
        f"All SSL verification attempts failed: {'; '.join(errors)}"
    )
