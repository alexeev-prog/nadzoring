"""Email security record analysis (SPF, DKIM, DMARC)."""

import re
import subprocess
from dataclasses import dataclass, field
from logging import Logger
from typing import Any

import dns.resolver
from dns.resolver import Answer

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_DKIM_SELECTORS: tuple[str, ...] = (
    "default",
    "google",
    "k1",
    "mail",
    "dkim",
    "selector1",
    "selector2",
    "s1",
    "s2",
    "smtp",
    "email",
    "mx",
    "key1",
)


@dataclass
class SpfResult:
    """
    SPF record analysis result.

    Attributes:
        found: Whether an SPF record was found.
        record: The raw SPF TXT record string.
        mechanisms: Extracted mechanisms (e.g. ``include:``, ``ip4:``).
        all_qualifier: The catch-all qualifier (``-``, ``~``, ``+``, ``?``).
        issues: List of detected configuration issues.

    """

    found: bool = False
    record: str | None = None
    mechanisms: list[str] = field(default_factory=list)
    all_qualifier: str | None = None
    issues: list[str] = field(default_factory=list)


@dataclass
class DkimResult:
    """
    DKIM record analysis result.

    Attributes:
        found: Whether at least one DKIM record was found.
        records: Mapping of selector to raw DKIM TXT record.
        selectors_checked: All selectors that were probed.
        issues: List of detected configuration issues.

    """

    found: bool = False
    records: dict[str, str] = field(default_factory=dict)
    selectors_checked: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class DmarcResult:
    """
    DMARC record analysis result.

    Attributes:
        found: Whether a DMARC record was found.
        record: The raw DMARC TXT record string.
        policy: The ``p=`` policy value (``none``, ``quarantine``, ``reject``).
        subdomain_policy: The ``sp=`` subdomain policy value.
        pct: The ``pct=`` percentage value.
        rua: Aggregate report addresses.
        ruf: Forensic report addresses.
        issues: List of detected configuration issues.

    """

    found: bool = False
    record: str | None = None
    policy: str | None = None
    subdomain_policy: str | None = None
    pct: int | None = None
    rua: list[str] = field(default_factory=list)
    ruf: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def _join_txt_chunks(line: str) -> str:
    """
    Join multiple quoted chunks from a single TXT record line.

    ``dig +short TXT`` represents long TXT records as multiple quoted
    strings on one line, e.g. ``"v=spf1 include:foo" "~all"``.
    This function extracts all quoted chunks and concatenates them.
    If no quoted chunks are found the raw line is returned stripped.

    Args:
        line: A single line of ``dig +short TXT`` output.

    Returns:
        The full TXT record value as a single string.

    """
    parts: list[str] = re.findall(r'"((?:[^"\\]|\\.)*)"', line)
    return "".join(parts) if parts else line.strip()


def _query_txt(name: str) -> list[str]:
    """
    Retrieve TXT records for a DNS name.

    Tries ``dnspython`` first, then falls back to the system ``dig``
    command, then ``nslookup``.  Multi-chunk TXT records (where a single
    record is split across several quoted strings) are joined into one
    value before being returned.

    Args:
        name: Fully qualified DNS name to query.

    Returns:
        List of complete TXT record strings, one entry per DNS record.

    """
    try:
        answers: Answer = dns.resolver.resolve(name, "TXT", lifetime=5)
        return [b"".join(r.strings).decode("utf-8", errors="replace") for r in answers]
    except Exception:
        logger.debug(
            "dnspython TXT lookup failed for %s.\n"
            "Falling back to system tools (dig/nslookup).\n"
            "If this persists, install dnspython: pip install dnspython",
            name,
        )

    try:
        output: str = subprocess.check_output(
            ["dig", "+short", "TXT", name],
            stderr=subprocess.DEVNULL,
            timeout=10,
            text=True,
        )
        return [_join_txt_chunks(line) for line in output.splitlines() if line.strip()]
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        pass

    try:
        output = subprocess.check_output(
            ["nslookup", "-type=TXT", name],
            stderr=subprocess.DEVNULL,
            timeout=10,
            text=True,
        )
        records: list[str] = []
        for line in output.splitlines():
            if "text =" in line.lower():
                raw: str = line.split("=", 1)[1].strip()
                records.append(_join_txt_chunks(raw))
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return []
    else:
        return records


def _analyse_spf(domain: str) -> SpfResult:
    """
    Analyse the SPF record for a domain.

    Args:
        domain: The domain to query.

    Returns:
        Populated :class:`SpfResult` instance.

    """
    result = SpfResult()
    records: list[str] = _query_txt(domain)
    spf_records: list[str] = [r for r in records if r.startswith("v=spf1")]

    if not spf_records:
        result.issues.append("No SPF record found")
        return result

    if len(spf_records) > 1:
        result.issues.append("Multiple SPF records found (RFC violation)")

    record: str = spf_records[0]
    result.found = True
    result.record = record

    parts: list[str] = record.split()
    result.mechanisms = [p for p in parts[1:] if not p.startswith("all")]

    for part in parts:
        if part in {"-all", "~all", "+all", "?all"} or part == "all":
            result.all_qualifier = part[0] if len(part) > 3 else "+"
            if result.all_qualifier == "+":
                result.issues.append("+all allows any sender (insecure)")

    if result.all_qualifier is None:
        result.issues.append("Missing 'all' mechanism")

    lookup_count: int = sum(
        1
        for m in result.mechanisms
        if any(m.startswith(p) for p in ("include:", "a", "mx", "ptr", "exists:"))
    )
    if lookup_count > 10:
        result.issues.append(f"Exceeds 10 DNS lookup limit ({lookup_count} lookups)")

    return result


def _analyse_dkim(domain: str) -> DkimResult:
    """
    Probe common DKIM selectors for a domain.

    Args:
        domain: The domain to check.

    Returns:
        Populated :class:`DkimResult` instance.

    """
    result = DkimResult(selectors_checked=list(_DKIM_SELECTORS))

    for selector in _DKIM_SELECTORS:
        name: str = f"{selector}._domainkey.{domain}"
        records: list[str] = _query_txt(name)
        dkim_records: list[str] = [r for r in records if "v=DKIM1" in r or "p=" in r]
        if dkim_records:
            result.found = True
            result.records[selector] = dkim_records[0]

    if not result.found:
        result.issues.append("No DKIM records found for common selectors")

    return result


def _analyse_dmarc(domain: str) -> DmarcResult:  # noqa: C901
    """
    Analyse the DMARC record for a domain.

    Args:
        domain: The domain to check.

    Returns:
        Populated :class:`DmarcResult` instance.

    """
    result = DmarcResult()
    name: str = f"_dmarc.{domain}"
    records: list[str] = _query_txt(name)
    dmarc_records: list[str] = [r for r in records if r.startswith("v=DMARC1")]

    if not dmarc_records:
        result.issues.append("No DMARC record found")
        return result

    result.found = True
    result.record = dmarc_records[0]

    tags: dict[str, str] = {}
    for token in result.record.split(";"):
        token = token.strip()  # noqa: PLW2901
        if "=" in token:
            k, _, v = token.partition("=")
            tags[k.strip().lower()] = v.strip()

    result.policy = tags.get("p")
    result.subdomain_policy = tags.get("sp")

    pct_raw: str | None = tags.get("pct")
    if pct_raw is not None:
        try:
            result.pct = int(pct_raw)
        except ValueError:
            result.issues.append(f"Invalid pct value: {pct_raw!r}")

    rua_raw: str | None = tags.get("rua")
    if rua_raw:
        result.rua = [addr.strip() for addr in rua_raw.split(",")]

    ruf_raw: str | None = tags.get("ruf")
    if ruf_raw:
        result.ruf = [addr.strip() for addr in ruf_raw.split(",")]

    if result.policy is None:
        result.issues.append("Missing policy tag (p=)")
    elif result.policy == "none":
        result.issues.append("Policy p=none does not protect against spoofing")

    if not result.rua:
        result.issues.append("No aggregate report address (rua=) configured")

    if result.pct is not None and result.pct < 100:
        result.issues.append(
            f"Policy applies to only {result.pct}% of messages (pct={result.pct})"
        )

    return result


def check_email_security(domain: str) -> dict[str, Any]:
    """
    Check email security configuration for a domain.

    Analyses SPF, DKIM (probing common selectors), and DMARC records and
    returns a structured summary of findings and issues.

    Args:
        domain: The domain to evaluate (e.g. ``"example.com"``).

    Returns:
        Dictionary with the following keys:

        - ``domain`` (str): The queried domain.
        - ``spf`` (dict): SPF analysis with keys ``found``, ``record``,
          ``mechanisms``, ``all_qualifier``, ``issues``.
        - ``dkim`` (dict): DKIM analysis with keys ``found``, ``records``,
          ``selectors_checked``, ``issues``.
        - ``dmarc`` (dict): DMARC analysis with keys ``found``, ``record``,
          ``policy``, ``subdomain_policy``, ``pct``, ``rua``, ``ruf``,
          ``issues``.
        - ``overall_score`` (int): Simple 0-3 score counting how many of
          SPF/DKIM/DMARC were found.
        - ``all_issues`` (list[str]): Concatenation of issues from all
          three checks.

    Examples:
        >>> result = check_email_security("example.com")
        >>> result["spf"]["found"]
        True
        >>> result["dmarc"]["policy"]
        'reject'

    """
    spf: SpfResult = _analyse_spf(domain)
    dkim: DkimResult = _analyse_dkim(domain)
    dmarc: DmarcResult = _analyse_dmarc(domain)

    all_issues: list[str] = spf.issues + dkim.issues + dmarc.issues
    score: int = sum([spf.found, dkim.found, dmarc.found])

    return {
        "domain": domain,
        "spf": {
            "found": spf.found,
            "record": spf.record,
            "mechanisms": spf.mechanisms,
            "all_qualifier": spf.all_qualifier,
            "issues": spf.issues,
        },
        "dkim": {
            "found": dkim.found,
            "records": dkim.records,
            "selectors_checked": dkim.selectors_checked,
            "issues": dkim.issues,
        },
        "dmarc": {
            "found": dmarc.found,
            "record": dmarc.record,
            "policy": dmarc.policy,
            "subdomain_policy": dmarc.subdomain_policy,
            "pct": dmarc.pct,
            "rua": dmarc.rua,
            "ruf": dmarc.ruf,
            "issues": dmarc.issues,
        },
        "overall_score": score,
        "all_issues": all_issues,
    }
