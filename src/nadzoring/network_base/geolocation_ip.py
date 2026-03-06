"""Geographic IP lookup via ip-api.com."""

from logging import Logger

from requests import RequestException, Response, get

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_GEO_API_URL = "http://ip-api.com/json/{ip}"
_GEO_FIELDS = "lat,lon,country,city,status,message"


def geo_ip(ip: str) -> dict[str, str]:
    """
    Retrieve geographic information for a given public IP address.

    Queries the ip-api.com JSON API and returns a flat dictionary with
    location data. Returns an empty dict on any network or parse error.

    Args:
        ip: IPv4 or IPv6 address to geolocate.

    Returns:
        Dictionary with string keys ``lat``, ``lon``, ``country``, and
        ``city`` when the lookup succeeds, or an empty dict on failure.

    Examples:
        >>> result = geo_ip("8.8.8.8")
        >>> "lat" in result and "lon" in result
        True

    """
    try:
        response: Response = get(
            url=_GEO_API_URL.format(ip=ip),
            params={"fields": _GEO_FIELDS},
            timeout=10,
        )
        response.raise_for_status()
        data: dict = response.json()
    except (RequestException, ValueError):
        logger.exception("Failed to geolocate IP %s", ip)
        return {}

    if data.get("status") == "fail":
        logger.warning("ip-api.com rejected query for %s: %s", ip, data.get("message"))
        return {}

    return {
        "lat": str(data.get("lat", "")),
        "lon": str(data.get("lon", "")),
        "country": str(data.get("country", "")),
        "city": str(data.get("city", "")),
    }
