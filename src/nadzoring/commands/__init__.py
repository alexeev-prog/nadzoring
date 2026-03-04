"""Command modules initialization."""

from nadzoring.commands.arp_commands import arp_group
from nadzoring.commands.dns_commands import dns_group
from nadzoring.commands.network_commands import network_group

__all__ = [
    "arp_group",
    "dns_group",
    "network_group",
]
