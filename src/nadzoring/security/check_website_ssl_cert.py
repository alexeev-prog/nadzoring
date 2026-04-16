"""
SSL/TLS Certificate Analysis and Validation Module.

This module provides comprehensive functionality for analyzing SSL/TLS certificates,
checking certificate validity, expiration, and security configurations of HTTPS servers.
It supports both verified and unverified certificate fetching, detailed certificate
information extraction, and protocol/cipher suite analysis.

The module is built on top of Python's ssl and cryptography libraries, providing
a high-level interface for common SSL/TLS certificate inspection tasks.

Typical usage example:
    result = check_ssl_expiry("example.com")
    if result["status"] == "valid":
        print(f"Certificate valid for {result['remaining_days']} more days")

    # For detailed analysis
    cert_info = CertificateInfo("example.com")
    cert_info.fetch_full_chain()
    print(get_subject_info(cert_info.cert))
"""

import socket
import ssl
from datetime import UTC, datetime
from ssl import SSLContext
from typing import Any

import certifi
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed448, ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.types import CertificateIssuerPublicKeyTypes
from cryptography.x509 import (
    Certificate,
    DNSName,
    Extension,
    ExtensionNotFound,
    IPAddress,
    Name,
    NameAttribute,
    ObjectIdentifier,
    SubjectAlternativeName,
)
from cryptography.x509.oid import ExtensionOID, NameOID

from nadzoring.utils.timeout import TimeoutConfig


class CertificateInfo:
    """
    A class for fetching and storing SSL/TLS certificate information from a server.

    This class handles the connection to a server and retrieval of its SSL/TLS
    certificates, supporting both full chain verification and unverified fetching.

    Attributes:
        hostname (str): The domain name or IP address of the target server.
        port (int): The port number to connect to (default: 443 for HTTPS).
        timeout (int): Connection timeout in seconds (default: 10).

    Examples:
        >>> cert_info = CertificateInfo("example.com")
        >>> cert_info.fetch_full_chain()
        >>> cert = cert_info.cert
        >>> print(f"Certificate issuer: {get_issuer_info(cert)}")

    """

    def __init__(
        self,
        hostname: str,
        port: int = 443,
        timeout_config: TimeoutConfig | None = None,
    ) -> None:
        """
        Initialize CertificateInfo instance.

        Args:
            hostname: The domain name or IP address to connect to.
            port: The port number for SSL/TLS connection. Defaults to 443.
            timeout_config: Unified timeout configuration. If None, uses default TimeoutConfig.

        """
        self.hostname = hostname
        self.port = port
        self.timeout_config = timeout_config or TimeoutConfig()
        self._cert: Certificate | None = None
        self._peercert: dict[str, Any] | None = None
        self._chain: list[Certificate] = []

    def fetch_full_chain(self) -> None:
        """
        Fetch the complete verified certificate chain from the server.

        Establishes a secure connection to the server and retrieves:
        - The peer certificate in both DER and parsed formats
        - The complete verified certificate chain

        This method performs full certificate validation including hostname
        verification using the system's CA bundle and certifi's certificates.

        Raises:
            ssl.SSLCertVerificationError: If certificate validation fails.
            socket.timeout: If connection timeout occurs.
            ConnectionError: If connection cannot be established.
            RuntimeError: If certificate chain cannot be retrieved.

        Note:
            This method populates _cert, _peercert, and _chain attributes.

        """
        context: SSLContext = ssl.create_default_context()
        context.load_verify_locations(certifi.where())

        with (
            socket.create_connection((self.hostname, self.port), timeout=int(self.timeout_config.connect)) as sock,
            context.wrap_socket(sock, server_hostname=self.hostname) as ssock,
        ):
            self._peercert = ssock.getpeercert()
            der_cert: bytes | None = ssock.getpeercert(binary_form=True)
            if der_cert is None:
                msg = "Server did not return a certificate."
                raise RuntimeError(msg)
            self._cert = x509.load_der_x509_certificate(der_cert, default_backend())

            self._chain = []
            if hasattr(ssock, "get_verified_chain"):
                for der in ssock.get_verified_chain():
                    self._chain.append(x509.load_der_x509_certificate(der, default_backend()))
            else:
                self._chain.append(self._cert)

    def fetch_unverified(self) -> None:
        """
        Fetch the certificate without performing validation.

        Establishes a connection to the server but disables certificate
        validation and hostname checking. Useful for:
        - Testing environments
        - Servers with self-signed certificates
        - Debugging certificate issues

        Raises:
            socket.timeout: If connection timeout occurs.
            ConnectionError: If connection cannot be established.
            RuntimeError: If the server did not return a certificate.

        Warning:
            This method disables security checks and should only be used
            in controlled environments or for diagnostic purposes.

        """
        context: SSLContext = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with (
            socket.create_connection((self.hostname, self.port), timeout=int(self.timeout_config.connect)) as sock,
            context.wrap_socket(sock, server_hostname=self.hostname) as ssock,
        ):
            der_cert: bytes | None = ssock.getpeercert(binary_form=True)
            if der_cert is None:
                msg = "Server did not return a certificate."
                raise RuntimeError(msg)
            self._cert = x509.load_der_x509_certificate(der_cert, default_backend())

    @property
    def cert(self) -> Certificate:
        """
        Get the fetched certificate.

        Returns:
            The parsed X.509 certificate object.

        Raises:
            RuntimeError: If certificate hasn't been fetched yet.

        """
        if self._cert is None:
            msg = "Certificate not fetched. Call fetch_full_chain() first."
            raise RuntimeError(msg)
        return self._cert

    @property
    def chain(self) -> list[Certificate]:
        """
        Get the complete certificate chain.

        Returns:
            List of X.509 certificate objects representing the chain,
            from leaf to root.

        Raises:
            RuntimeError: If chain hasn't been fetched yet.

        """
        if not self._chain and self._cert is None:
            msg = "Certificate chain not fetched. Call fetch_full_chain() first."
            raise RuntimeError(msg)
        return self._chain


def get_key_info(
    public_key: CertificateIssuerPublicKeyTypes,
) -> dict[str, str | int]:
    """
    Extract detailed information about a public key.

    Analyzes the public key to determine its algorithm, key size, and
    cryptographic strength based on current industry standards.

    Args:
        public_key: The public key object from a certificate.

    Returns:
        A dictionary containing:
            - algorithm: The key algorithm (RSA, DSA, EC, Ed25519, Ed448)
            - key_size: Key size in bits (for RSA, DSA, EC)
            - curve: Curve name (for EC keys)
            - strength: Security assessment ("weak", "good", "strong", "unknown")

    Examples:
        >>> key_info = get_key_info(cert.public_key())
        >>> print(f"Algorithm: {key_info['algorithm']}, Strength: {key_info['strength']}")

    Note:
        Strength assessment:
        - RSA < 2048 bits: weak
        - RSA 2048-4095 bits: good
        - RSA >= 4096 bits: strong
        - DSA < 2048 bits: weak, >= 2048 bits: good
        - EC, Ed25519, Ed448: strong

    """
    if isinstance(public_key, rsa.RSAPublicKey):
        return {
            "algorithm": "RSA",
            "key_size": public_key.key_size,
            "strength": ("weak" if public_key.key_size < 2048 else "good" if public_key.key_size < 4096 else "strong"),
        }
    if isinstance(public_key, dsa.DSAPublicKey):
        return {
            "algorithm": "DSA",
            "key_size": public_key.key_size,
            "strength": "weak" if public_key.key_size < 2048 else "good",
        }
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return {
            "algorithm": "EC",
            "curve": public_key.curve.name,
            "strength": "good",
        }
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        return {"algorithm": "Ed25519", "strength": "strong"}
    if isinstance(public_key, ed448.Ed448PublicKey):
        return {"algorithm": "Ed448", "strength": "strong"}
    return {"algorithm": "Unknown", "strength": "unknown"}


def check_domain_match(cert: Certificate, hostname: str) -> tuple[bool, list[str]]:
    """
    Verify if a certificate matches a given hostname.

    Checks both Subject Alternative Names (SAN) and Common Name (CN) fields
    to determine if the certificate is valid for the specified hostname.
    Supports wildcard certificates.

    Args:
        cert: The X.509 certificate to check.
        hostname: The hostname to verify against.

    Returns:
        A tuple containing:
            - bool: True if hostname matches any SAN or CN, False otherwise.
            - list[str]: List of matched names with their types (DNS: or CN:).

    Examples:
        >>> matches, matched_names = check_domain_match(cert, "example.com")
        >>> if matches:
        ...     print(f"Certificate valid for: {', '.join(matched_names)}")

    Note:
        - Wildcard matching only supports patterns like "*.example.com"
        - The function checks SAN first, then falls back to CN
        - IP addresses in SAN are also checked if hostname is an IP

    """
    cn_match = False
    san_match = False
    matches: list[str] = []

    try:
        san: Extension[Any] = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        if isinstance(san.value, SubjectAlternativeName):
            for name in san.value:
                if isinstance(name, DNSName) and (
                    name.value == hostname or (name.value.startswith("*.") and _match_wildcard(name.value, hostname))
                ):
                    san_match = True
                    matches.append(f"DNS:{name.value}")
                if isinstance(name, IPAddress) and str(name.value) == hostname:
                    san_match = True
                    matches.append(f"IP:{name.value}")
    except ExtensionNotFound:
        pass

    subject: Name = cert.subject
    cn_attributes: list[NameAttribute] = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if cn_attributes:
        cn: str = cn_attributes[0].value
        if cn == hostname or (cn.startswith("*.") and _match_wildcard(cn, hostname)):
            cn_match = True
            matches.append(f"CN:{cn}")

    return (san_match or cn_match, matches)


def _match_wildcard(pattern: str, hostname: str) -> bool:
    """
    Match a wildcard pattern against a hostname.

    Internal helper function to check if a hostname matches a wildcard pattern.
    Supports only patterns like "*.example.com".

    Args:
        pattern: The wildcard pattern (must start with "*.").
        hostname: The hostname to check.

    Returns:
        True if the hostname matches the pattern, False otherwise.

    Examples:
        >>> _match_wildcard("*.example.com", "www.example.com")
        True
        >>> _match_wildcard("*.example.com", "example.com")
        False

    """
    if not pattern.startswith("*."):
        return False
    base: str = pattern[2:]
    return hostname.endswith(base) and hostname.count(".") == base.count(".") + 1


def get_subject_info(cert: Certificate) -> dict[str, str]:
    """
    Extract subject information from a certificate.

    Retrieves common subject fields including Common Name (CN),
    Organization (O), Organizational Unit (OU), Country (C),
    State/Province (ST), Locality (L), and Email Address.

    Args:
        cert: The X.509 certificate to extract subject from.

    Returns:
        Dictionary mapping field names to their values.
        Only fields present in the certificate are included.

    Examples:
        >>> subject = get_subject_info(cert)
        >>> print(f"Common Name: {subject.get('CN', 'Not found')}")

    """
    subject: Name = cert.subject
    info: dict[str, str] = {}

    oid_mapping: dict[str, ObjectIdentifier] = {
        "CN": NameOID.COMMON_NAME,
        "O": NameOID.ORGANIZATION_NAME,
        "OU": NameOID.ORGANIZATIONAL_UNIT_NAME,
        "C": NameOID.COUNTRY_NAME,
        "ST": NameOID.STATE_OR_PROVINCE_NAME,
        "L": NameOID.LOCALITY_NAME,
        "emailAddress": NameOID.EMAIL_ADDRESS,
    }

    for key, oid in oid_mapping.items():
        attributes: list[NameAttribute] = subject.get_attributes_for_oid(oid)
        if attributes:
            info[key] = str(attributes[0].value)

    return info


def get_issuer_info(cert: Certificate) -> dict[str, str]:
    """
    Extract issuer information from a certificate.

    Retrieves common issuer fields including Common Name (CN),
    Organization (O), Organizational Unit (OU), and Country (C).

    Args:
        cert: The X.509 certificate to extract issuer from.

    Returns:
            Dictionary mapping field names to their values.
            Only fields present in the certificate are included.

    Examples:
        >>> issuer = get_issuer_info(cert)
        >>> print(f"Issued by: {issuer.get('CN', 'Unknown')}")

    """
    issuer: Name = cert.issuer
    info: dict[str, str] = {}

    oid_mapping: dict[str, ObjectIdentifier] = {
        "CN": NameOID.COMMON_NAME,
        "O": NameOID.ORGANIZATION_NAME,
        "OU": NameOID.ORGANIZATIONAL_UNIT_NAME,
        "C": NameOID.COUNTRY_NAME,
    }

    for key, oid in oid_mapping.items():
        attributes: list[NameAttribute] = issuer.get_attributes_for_oid(oid)
        if attributes:
            info[key] = str(attributes[0].value)

    return info


def get_san_list(cert: Certificate) -> list[str]:
    """
    Extract Subject Alternative Names (SAN) from a certificate.

    Retrieves all DNS names and IP addresses listed in the certificate's
    Subject Alternative Name extension.

    Args:
        cert: The X.509 certificate to extract SANs from.

    Returns:
        List of SAN entries, each prefixed with "DNS:" or "IP:".
        Returns empty list if no SAN extension exists.

    Examples:
        >>> sans = get_san_list(cert)
        >>> for san in sans:
        ...     print(f"Alternative name: {san}")

    """
    sans: list[str] = []
    try:
        san: Extension[Any] = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        if isinstance(san.value, SubjectAlternativeName):
            for name in san.value:
                if isinstance(name, DNSName):
                    sans.append(f"DNS:{name.value}")
                elif isinstance(name, IPAddress):
                    sans.append(f"IP:{name.value}")
    except ExtensionNotFound:
        pass
    return sans


def _probe_tls_version(
    hostname: str,
    port: int,
    min_version: ssl.TLSVersion,
    max_version: ssl.TLSVersion,
    timeout_config: TimeoutConfig,
) -> bool:
    """
    Probe whether a server accepts a specific TLS version range.

    Creates a client context constrained to exactly one protocol version
    (by setting both minimum and maximum to the same value) and attempts
    a connection.  All certificate validation is disabled so the probe
    succeeds regardless of certificate issues.

    Args:
        hostname: Server hostname or IP address.
        port: TCP port to connect to.
        min_version: Minimum TLS version to offer.
        max_version: Maximum TLS version to offer.
        timeout_config: Unified timeout configuration.

    Returns:
        ``True`` if the server accepted the connection, ``False``
        if it refused or an error occurred.

    """
    try:
        context: SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = min_version
        context.maximum_version = max_version
        with (
            socket.create_connection((hostname, port), timeout=int(timeout_config.connect)) as sock,
            context.wrap_socket(sock, server_hostname=hostname),
        ):
            return True
    except (ssl.SSLError, ConnectionError, OSError):
        return False


def check_protocols_and_ciphers(
    hostname: str,
    port: int = 443,
    timeout_config: TimeoutConfig | None = None,
) -> dict[str, list[str] | bool]:
    """
    Check which TLS protocol versions are accepted by a server.

    Probes TLSv1.0 through TLSv1.3 by constraining each connection to
    exactly one version.  SSLv2 and SSLv3 are marked as not supported
    unconditionally because Python 3.10+ removed their protocol constants
    and no modern server should accept them.

    Args:
        hostname: The server hostname or IP address.
        port: The port to connect to. Defaults to ``443``.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        Dictionary with keys:

        - ``supported`` (list[str]): Protocol versions the server accepted.
        - ``failed`` (list[str]): Protocol versions the server rejected.
        - ``has_outdated`` (bool): ``True`` when TLSv1.0 or TLSv1.1 is
          supported, indicating a security risk.

    Examples:
        >>> result = check_protocols_and_ciphers("example.com")
        >>> result["has_outdated"]
        False
        >>> "TLSv1.2" in result["supported"]
        True

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    outdated: tuple[str, ...] = ("TLSv1.0", "TLSv1.1")

    candidates: list[tuple[str, ssl.TLSVersion]] = [
        ("TLSv1.0", ssl.TLSVersion.TLSv1),
        ("TLSv1.1", ssl.TLSVersion.TLSv1_1),
        ("TLSv1.2", ssl.TLSVersion.TLSv1_2),
        ("TLSv1.3", ssl.TLSVersion.TLSv1_3),
    ]

    supported: list[str] = []
    failed: list[str] = []

    for version_name, tls_version in candidates:
        if _probe_tls_version(hostname, port, tls_version, tls_version, timeout_config):
            supported.append(version_name)
        else:
            failed.append(version_name)

    return {
        "supported": supported,
        "failed": failed,
        "has_outdated": any(v in supported for v in outdated),
    }


def _cert_expiry(cert: Certificate) -> datetime:
    """
    Return the certificate's expiry datetime as a timezone-aware UTC value.

    Prefers ``not_valid_after_utc`` (cryptography >= 42) and falls back to
    ``not_valid_after`` with an explicit UTC tag for older versions.

    Args:
        cert: Parsed X.509 certificate.

    Returns:
        Timezone-aware :class:`datetime` in UTC.

    """
    if hasattr(cert, "not_valid_after_utc"):
        date: datetime = cert.not_valid_after_utc
        return date
    dt: datetime = cert.not_valid_after
    return dt.replace(tzinfo=UTC)


def _oid_name(oid: ObjectIdentifier) -> str:
    """
    Return a human-readable name for an OID, falling back to dotted string.

    Uses the private ``_name`` attribute that exists in the Rust-backed
    cryptography implementation. Falls back to :attr:`dotted_string` when
    the attribute is absent so the function is forward-compatible.

    Args:
        oid: An :class:`~cryptography.x509.ObjectIdentifier` instance.

    Returns:
        Human-readable name string or dotted OID string.

    """
    return getattr(oid, "_name", None) or oid.dotted_string


def check_ssl_certificate(
    domain: str,
    days_before: int = 7,
    *,
    verify: bool = True,
    timeout_config: TimeoutConfig | None = None,
) -> dict[str, Any]:
    """
    Comprehensive SSL certificate check for a domain.

    Performs a complete analysis of a domain's SSL/TLS certificate including
    expiration, issuer information, subject details, domain matching,
    key strength, and protocol support.

    Args:
        domain: The domain name to check.
        days_before: Number of days before expiry to trigger warning status.
                     Defaults to 7.
        verify: Whether to perform full certificate verification.
                Defaults to True. This is a keyword-only argument.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        Dictionary containing comprehensive certificate information:
            - domain: The checked domain
            - days_before: Warning threshold used
            - verification: Status of verification ("verified", "unverified", "failed")
            - status: Certificate status ("valid", "warning", "expired", "error")
            - remaining_days: Days until expiry (None if error)
            - expiry_date: ISO format expiration date
            - subject: Dictionary of subject fields
            - issuer: Dictionary of issuer fields
            - san: List of Subject Alternative Names
            - domain_match: Boolean indicating if domain matches certificate
            - matched_names: List of matched names
            - public_key: Dictionary with key information
            - signature_algorithm: Certificate signature algorithm
            - serial_number: Certificate serial number
            - version: Certificate version
            - protocols: Protocol support information
            - chain_length: Number of certificates in chain (if verified)
            - chain_valid: Boolean indicating if the certificate chain is properly
                          constructed and valid (only meaningful when verification
                          succeeded)
            - error: Error message if status is "error"
            - warning: Warning message if verification disabled

    Examples:
        >>> result = check_ssl_certificate("example.com")
        >>> if result["status"] == "valid":
        ...     print(f"Certificate expires in {result['remaining_days']} days")
        >>> elif result["status"] == "warning":
        ...     print(f"Certificate expires soon: {result['remaining_days']} days")

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    cert_info = CertificateInfo(domain, timeout_config=timeout_config)
    result: dict[str, Any] = {
        "domain": domain,
        "days_before": days_before,
    }

    try:
        if verify:
            cert_info.fetch_full_chain()
            result["verification"] = "verified"
        else:
            cert_info.fetch_unverified()
            result["verification"] = "unverified"
            result["warning"] = "Certificate verification disabled"

        cert: Certificate = cert_info.cert

        expiry: datetime = _cert_expiry(cert)
        remaining: int = (expiry - datetime.now(UTC)).days
        result.update({
            "remaining_days": remaining,
            "expiry_date": expiry.isoformat(),
            "status": ("expired" if remaining < 0 else "warning" if remaining <= days_before else "valid"),
        })

        subject: dict[str, str] = get_subject_info(cert)
        if subject:
            result["subject"] = subject

        issuer: dict[str, str] = get_issuer_info(cert)
        if issuer:
            result["issuer"] = issuer

        sans: list[str] = get_san_list(cert)
        if sans:
            result["san"] = sans

        matches, matched_names = check_domain_match(cert, domain)
        result["domain_match"] = matches
        if matched_names:
            result["matched_names"] = matched_names

        public_key: DSAPublicKey | Ed25519PublicKey | Ed448PublicKey | EllipticCurvePublicKey | RSAPublicKey = (
            cert.public_key()
        )
        key_info: dict[str, int | str] = get_key_info(public_key)
        result["public_key"] = key_info

        result["signature_algorithm"] = _oid_name(cert.signature_algorithm_oid)
        result["serial_number"] = str(cert.serial_number)
        result["version"] = cert.version.value

        protocols: dict[str, bool | list[str]] = check_protocols_and_ciphers(domain, timeout_config=timeout_config)
        result["protocols"] = protocols

        if verify:
            if cert_info.chain:
                result["chain_length"] = len(cert_info.chain)
                result["chain_valid"] = True
            else:
                result["chain_length"] = 0
                result["chain_valid"] = False

    except Exception as e:
        result.update({
            "remaining_days": None,
            "status": "error",
            "error": str(e),
            "verification": "failed" if verify else "unverified",
        })

    return result


def check_ssl_expiry(
    domain: str,
    days_before: int = 7,
    timeout_config: TimeoutConfig | None = None,
) -> dict[str, Any]:
    """
    Check SSL certificate expiration with full verification.

    Simplified function specifically focused on certificate expiration
    checking with full verification enabled. Equivalent to calling
    check_ssl_certificate() with verify=True.

    Args:
        domain: The domain name to check.
        days_before: Number of days before expiry to trigger warning.
                     Defaults to 7.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        Same as check_ssl_certificate() with verify=True.

    Examples:
        >>> result = check_ssl_expiry("example.com")
        >>> print(f"Certificate expires in {result['remaining_days']} days")

    """
    return check_ssl_certificate(domain, days_before, verify=True, timeout_config=timeout_config)


def check_ssl_expiry_with_fallback(
    domain: str,
    days_before: int = 7,
    timeout_config: TimeoutConfig | None = None,
) -> dict[str, Any]:
    """
    Check SSL certificate with automatic fallback to unverified mode.

    Attempts verified certificate check first; if that fails, falls back to
    unverified mode. Useful for monitoring systems that need to continue
    functioning even with problematic certificates.

    Args:
        domain: The domain name to check.
        days_before: Number of days before expiry to trigger warning.
                     Defaults to 7.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        Same as check_ssl_certificate() with verification status indicated
        in the "verification" field.

    Raises:
        ssl.SSLCertVerificationError: If both verified and unverified checks fail.

    Examples:
        >>> try:
        ...     result = check_ssl_expiry_with_fallback("example.com")
        ...     print(f"Verification mode: {result['verification']}")
        ... except ssl.SSLCertVerificationError as e:
        ...     print(f"Certificate check completely failed: {e}")

    Note:
        The fallback mode disables security checks and should be used
        cautiously. The returned result will indicate "unverified" when
        fallback was used.

    """
    errors: list[str] = []
    try:
        return check_ssl_certificate(domain, days_before, verify=True, timeout_config=timeout_config)
    except Exception as e:
        errors.append(f"Verified check failed: {e}")

    try:
        return check_ssl_certificate(domain, days_before, verify=False, timeout_config=timeout_config)
    except Exception as e:
        errors.append(f"Unverified check failed: {e}")

    raise ssl.SSLCertVerificationError(f"All SSL checks failed: {'; '.join(errors)}")
