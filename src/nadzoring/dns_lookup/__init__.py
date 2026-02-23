"""DNS lookup module for domain name resolution and DNS record checking."""

from nadzoring.dns_lookup.dns_resolver import check_dns, resolve_dns, reverse_dns

__all__: list[str] = ["check_dns", "resolve_dns", "reverse_dns"]
