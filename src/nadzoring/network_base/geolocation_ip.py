from requests import get


def geo_ip(ip: str) -> dict[str, str]:
    """A function for getting coordinates based on an external IP address.

    Performs a request to the service, which transmits the address.
    In response, it receives JSON with coordinates and more
    (the rest of the data is not returned from the function).
    However, if necessary, it can be expanded.

    Args:
        ip (str): ip address

    Returns:
        dict[str, str] | None: dict with lat and lon or None
    """
    try:
        req = get(url=f"http://ip-api.com/json/{ip}").json()  # noqa: S113
        return {"lat": req["lat"], "lon": req["lon"]}
    except Exception:
        return {}
