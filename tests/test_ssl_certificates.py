"""Certificate inspection tests using local keys and mocked transports."""

import importlib
import ipaddress
import ssl
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed448, ed25519, rsa
from cryptography.x509.oid import NameOID

from nadzoring.utils.timeout import TimeoutConfig

certs = importlib.import_module("nadzoring.security.check_website_ssl_cert")


@pytest.fixture
def certificate():
    """Create a real self-signed certificate without network or filesystem I/O."""
    key = ed25519.Ed25519PrivateKey.generate()
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Example"),
    ])
    now = datetime.now(UTC)
    return (
        x509
        .CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(123)
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("example.com"),
                x509.DNSName("*.example.com"),
                x509.IPAddress(ipaddress.ip_address("192.0.2.1")),
            ]),
            critical=False,
        )
        .sign(key, None)
    )


@pytest.mark.parametrize("mode", ["chain", "legacy", "unverified", "missing", "missing_unverified"])
def test_certificate_fetch(monkeypatch, certificate, mode):
    """Fetch real DER bytes over fake sockets, including legacy chain support."""
    der = certificate.public_bytes(serialization.Encoding.DER)
    peer = MagicMock()
    peer.getpeercert.return_value = None if mode.startswith("missing") else der
    if mode == "legacy":
        del peer.get_verified_chain
    else:
        peer.get_verified_chain.return_value = [der]
    context = MagicMock()
    context.wrap_socket.return_value.__enter__.return_value = peer
    monkeypatch.setattr(certs.ssl, "create_default_context", Mock(return_value=context))
    connection = MagicMock()
    monkeypatch.setattr(certs.socket, "create_connection", connection)
    info = certs.CertificateInfo("example.com")
    with pytest.raises(RuntimeError, match="not fetched"):
        _ = info.cert
    with pytest.raises(RuntimeError, match="not fetched"):
        _ = info.chain
    fetch = info.fetch_unverified if "unverified" in mode else info.fetch_full_chain
    if mode.startswith("missing"):
        with pytest.raises(RuntimeError, match="did not return a certificate"):
            fetch()
    else:
        fetch()
        assert info.cert.serial_number == 123
        assert len(info.chain) == (0 if mode == "unverified" else 1)
    assert connection.call_args.args == (("example.com", 443),)


@pytest.mark.parametrize(
    "key,algorithm,strength",
    [
        (
            rsa.generate_private_key(public_exponent=65537, key_size=1024).public_key(),
            "RSA",
            "weak",
        ),
        (
            rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key(),
            "RSA",
            "good",
        ),
        (dsa.generate_private_key(key_size=1024).public_key(), "DSA", "weak"),
        (ec.generate_private_key(ec.SECP256R1()).public_key(), "EC", "good"),
        (ed25519.Ed25519PrivateKey.generate().public_key(), "Ed25519", "strong"),
        (ed448.Ed448PrivateKey.generate().public_key(), "Ed448", "strong"),
        (object(), "Unknown", "unknown"),
    ],
)
def test_public_key_info(key, algorithm, strength):
    """Identify supported key algorithms and strength classifications."""
    result = certs.get_key_info(key)
    assert result["algorithm"] == algorithm
    assert result["strength"] == strength


def test_certificate_names(certificate):
    """Read subject, issuer, SAN, wildcard DNS names, and IP addresses."""
    assert certs.get_subject_info(certificate) == {"CN": "example.com", "O": "Example"}
    assert certs.get_issuer_info(certificate) == {"CN": "example.com", "O": "Example"}
    assert certs.get_san_list(certificate) == [
        "DNS:example.com",
        "DNS:*.example.com",
        "IP:192.0.2.1",
    ]
    assert certs.check_domain_match(certificate, "example.com") == (
        True,
        ["DNS:example.com", "CN:example.com"],
    )
    assert certs.check_domain_match(certificate, "www.example.com") == (
        True,
        ["DNS:*.example.com"],
    )
    assert certs.check_domain_match(certificate, "192.0.2.1") == (
        True,
        ["IP:192.0.2.1"],
    )
    assert certs.check_domain_match(certificate, "unrelated.net") == (False, [])
    assert not certs._match_wildcard("example.com", "www.example.com")
    assert not certs._match_wildcard("*.example.com", "deep.www.example.com")
    empty = SimpleNamespace(subject=x509.Name([]), extensions=Mock())
    empty.extensions.get_extension_for_oid.side_effect = x509.ExtensionNotFound(
        "absent", x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    )
    assert certs.get_san_list(empty) == []
    assert certs.check_domain_match(empty, "example.com") == (False, [])


@pytest.mark.parametrize("failure", [False, True])
def test_tls_probe(monkeypatch, failure):
    """Probe exact protocol bounds through a fake TLS context."""
    context = MagicMock()
    monkeypatch.setattr(certs.ssl, "SSLContext", Mock(return_value=context))
    connection = MagicMock(side_effect=OSError() if failure else None)
    monkeypatch.setattr(certs.socket, "create_connection", connection)
    version = ssl.TLSVersion.TLSv1_2
    assert certs._probe_tls_version("example.com", 443, version, version, TimeoutConfig()) is not failure
    assert context.minimum_version == version
    assert context.maximum_version == version


def test_protocol_support(monkeypatch):
    """Separate accepted and rejected protocol versions."""
    monkeypatch.setattr(certs, "_probe_tls_version", Mock(side_effect=[True, False, True, False]))
    result = certs.check_protocols_and_ciphers("example.com")
    assert result == {
        "supported": ["TLSv1.0", "TLSv1.2"],
        "failed": ["TLSv1.1", "TLSv1.3"],
        "has_outdated": True,
    }


def test_certificate_compatibility_helpers(certificate):
    """Support both modern timezone-aware and legacy certificate dates."""
    assert certs._cert_expiry(certificate) == certificate.not_valid_after_utc
    old = SimpleNamespace(not_valid_after=datetime(2020, 1, 1))
    assert certs._cert_expiry(old) == datetime(2020, 1, 1, tzinfo=UTC)
    assert certs._oid_name(SimpleNamespace(dotted_string="1.2.3")) == "1.2.3"
    assert certs._oid_name(SimpleNamespace(_name="name", dotted_string="1.2.3")) == "name"


@pytest.mark.parametrize("verify,chain", [(True, True), (True, False), (False, False)])
def test_comprehensive_certificate_check(monkeypatch, certificate, verify, chain):
    """Compose parsed certificate metadata and verification status."""
    info = Mock(cert=certificate, chain=[certificate] if chain else [])
    monkeypatch.setattr(certs, "CertificateInfo", Mock(return_value=info))
    monkeypatch.setattr(
        certs,
        "check_protocols_and_ciphers",
        Mock(return_value={"supported": ["TLSv1.3"]}),
    )
    result = certs.check_ssl_certificate("example.com", verify=verify)
    assert result["status"] == "valid"
    assert result["domain_match"] is True
    assert result["serial_number"] == "123"
    if verify:
        info.fetch_full_chain.assert_called_once_with()
        assert result["chain_valid"] is chain
        assert result["chain_length"] == int(chain)
    else:
        info.fetch_unverified.assert_called_once_with()
        assert result["warning"] == "Certificate verification disabled"


@pytest.mark.parametrize(
    "failure,error",
    [
        (ssl.SSLCertVerificationError(), "Certificate verification failed"),
        (TimeoutError(), "Connection timeout"),
        (ssl.SSLError(), "SSL handshake failed"),
        (ConnectionError(), "Connection failed"),
        (
            RuntimeError("Server did not return a certificate"),
            "No certificate returned",
        ),
        (RuntimeError("other"), "SSL handshake failed"),
        (ValueError(), "SSL handshake failed"),
    ],
)
def test_safe_certificate_errors(monkeypatch, failure, error):
    """Convert certificate and transport failures to stable error results."""
    monkeypatch.setattr(certs, "check_ssl_certificate", Mock(side_effect=failure))
    result = certs.check_ssl_certificate_safe("example.com", verify=False)
    assert result["error"] == error
    assert result["status"] == "error"
    assert result["verification"] == "unverified"


def test_certificate_wrappers(monkeypatch):
    """Delegate safe, expiry, and fallback calls with verification preserved."""
    check = Mock(return_value={"status": "valid"})
    monkeypatch.setattr(certs, "check_ssl_certificate", check)
    assert certs.check_ssl_certificate_safe("example.com") == {"status": "valid"}
    assert certs.check_ssl_expiry("example.com") == {"status": "valid"}
    assert certs.check_ssl_expiry_with_fallback("example.com") == {"status": "valid"}
    check.side_effect = [ssl.SSLError(), {"status": "warning"}]
    assert certs.check_ssl_expiry_with_fallback("example.com") == {"status": "warning"}
    assert check.call_args.kwargs["verify"] is False
