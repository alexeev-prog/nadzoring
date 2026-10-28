"""Package self-management and environment diagnostics."""

from nadzoring.core.diagnostics import check_dependencies, check_network, check_permissions, doctor
from nadzoring.core.releases import changelog, current_version, update, version_info

__all__ = [
    "changelog",
    "check_dependencies",
    "check_network",
    "check_permissions",
    "current_version",
    "doctor",
    "update",
    "version_info",
]
