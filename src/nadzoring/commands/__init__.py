"""Command modules initialization."""

from nadzoring.commands.arp_commands import arp_group
from nadzoring.commands.completions_commands import completion_group
from nadzoring.commands.dns_commands import dns_group
from nadzoring.commands.network_commands import network_group
from nadzoring.commands.security_commands import security_group

__all__: list[str] = [
    "arp_group",
    "completion_group",
    "dns_group",
    "network_group",
    "security_group",
]
