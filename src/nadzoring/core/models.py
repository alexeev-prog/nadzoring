"""Shared, serializable diagnostic results and exit-code policy."""

from typing import Literal, TypedDict

type Status = Literal["ok", "warning", "error", "update-available"]


class CheckResult(TypedDict):
    """One diagnostic observation; errors are explicit even in machine output."""

    check: str
    status: Status
    detail: str
    error: str | None


def result(check: str, detail: str, status: Status = "ok") -> CheckResult:
    """Build a diagnostic row with a structured expected-failure field."""
    return {
        "check": check,
        "status": status,
        "detail": detail,
        "error": detail if status in {"warning", "error"} else None,
    }


def exit_code(rows: list[CheckResult]) -> int:
    """Return blocking errors before warnings, then update notifications."""
    statuses = {row["status"] for row in rows}
    if "error" in statuses:
        return 2
    if "warning" in statuses:
        return 1
    return 3 if "update-available" in statuses else 0
