"""Shared result type returned by every connector probe."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ProbeStatus = Literal["ok", "degraded", "unreachable", "error"]


@dataclass
class ProbeResult:
    """Result of a single connector probe.

    Attributes:
        status: High-level health status.
        latency_ms: Round-trip time in milliseconds, or ``None`` if the check
            did not complete a full round-trip.
        error: Machine-readable error string when the probe failed; ``None``
            on success.
        details: Optional free-form mapping of extra diagnostic fields
            (e.g. HTTP status code, TLS expiry days, k8s node count).
        raw: Unprocessed response payload for debugging; not intended for
            programmatic use.
    """

    status: ProbeStatus
    latency_ms: float | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    raw: Any = None

    @property
    def ok(self) -> bool:
        """Return ``True`` if the probe succeeded without errors."""
        return self.error is None and self.status == "ok"
