"""
Geographic IP lookup via ip-api.com.

Typical usage::

    from nadzoring.network_base.geolocation_ip import geo_ip

    result = geo_ip("8.8.8.8")
    if not result:
        print("Geolocation failed")
    else:
        print(result["country"])  # "United States"
        print(result["city"])  # "Mountain View"
        print(result["lat"])  # "37.386"
        print(result["lon"])  # "-122.0838"

"""

from logging import Logger

from requests import RequestException, Response, get

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_GEO_API_URL = "http://ip-api.com/json/{ip}"
_GEO_FIELDS = "lat,lon,country,city,status,message"
_REQUEST_TIMEOUT = 10

GeoResult = dict[str, str]
"""Dict with keys ``lat``, ``lon``, ``country``, ``city`` (all strings)."""


def _fetch_geo_data(ip: str) -> dict | None:
    """
    Fetch raw JSON from ip-api.com for *ip*.

    Args:
        ip: IPv4 or IPv6 address string.

    Returns:
        Parsed JSON dict on success, ``None`` on network or parse failure.

    """
    try:
        response: Response = get(
            url=_GEO_API_URL.format(ip=ip),
            params={"fields": _GEO_FIELDS},
            timeout=_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except (RequestException, ValueError):
        logger.exception("Failed to fetch geolocation data for IP %s", ip)
        return None


def _parse_geo_response(data: dict, ip: str) -> GeoResult | None:
    """
    Validate and extract fields from ip-api response dict.

    Args:
        data: Raw JSON dict from ip-api.com.
        ip: Original IP address (used for logging only).

    Returns:
        :data:`GeoResult` on success, ``None`` when the API signals
        failure.

    """
    if data.get("status") == "fail":
        logger.warning(
            "ip-api.com rejected query for %s: %s",
            ip,
            data.get("message"),
        )
        return None

    return {
        "lat": str(data.get("lat", "")),
        "lon": str(data.get("lon", "")),
        "country": str(data.get("country", "")),
        "city": str(data.get("city", "")),
    }


def geo_ip(ip: str) -> GeoResult:
    """
    Retrieve geographic information for a given public IP address.

    Queries the `ip-api.com <http://ip-api.com>`_ JSON API and returns a
    flat dictionary with location data.  Returns an empty dict on any
    network or parse error so that callers can use a simple truthiness
    check::

        result = geo_ip("8.8.8.8")
        if not result:
            # handle failure
            ...

    .. note::
        ip-api.com rate-limits free callers to 45 requests per minute.
        Private / reserved IP addresses (e.g. ``192.168.x.x``) will
        return an empty dict because the API rejects them.

    Args:
        ip: IPv4 or IPv6 address to geolocate.

    Returns:
        :data:`GeoResult` dict with string keys ``lat``, ``lon``,
        ``country``, and ``city`` when the lookup succeeds, or an empty
        dict ``{}`` on failure.

    Examples:
        Successful lookup::

            result = geo_ip("8.8.8.8")
            assert "lat" in result and "lon" in result
            print(f"{result['city']}, {result['country']}")

        Handling failure (private IP, network error, rate-limit)::

            result = geo_ip("192.168.1.1")
            if not result:
                print("Geolocation not available")

        Using results for logging / display::

            for ip in ["8.8.8.8", "1.1.1.1", "9.9.9.9"]:
                geo = geo_ip(ip)
                location = f"{geo['city']}, {geo['country']}" if geo else "unknown"
                print(f"{ip} → {location}")

    """
    raw: dict[str, str | int | float] | None = _fetch_geo_data(ip)
    if raw is None:
        return {}

    parsed: dict[str, str] | None = _parse_geo_response(raw, ip)
    return parsed or {}
