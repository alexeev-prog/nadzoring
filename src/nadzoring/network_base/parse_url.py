"""URL parsing utilities."""

from urllib.parse import ParseResult, parse_qsl, urlparse


def parse_url(url: str) -> dict[str, str | int | list[tuple[str, str]] | None]:
    """
    Parse a URL string and return its components as a dictionary.

    This function takes a URL string, parses it into its constituent parts,
    and returns a dictionary containing all the components. It also prints
    the parsed components to the console for visibility.

    Args:
        url (str): The URL string to parse. Can be any valid URL format.

    Returns:
        Dict[str, Union[str, int, List[Tuple[str, str]], None]]: A dictionary
        containing the parsed URL components with the following keys:
            - original: The original URL string
            - protocol: The URL scheme (e.g., 'http', 'https', 'ftp')
            - username: Username component if present in the URL
            - password: Password component if present in the URL
            - hostname: Domain name or IP address
            - port: Port number if specified (as integer)
            - path: URL path component
            - query: Raw query string
            - query_params: List of (key, value) tuples from parsed query string
            - fragment: URL fragment/hash component

    Example:
        >>> result = parse_url("https://user:pass@example.com:8080/path?key=value#section")
        original: https://user:pass@example.com:8080/path?key=value#section
        protocol: https
        username: user
        password: pass
        hostname: example.com
        port: 8080
        path: /path
        query: key=value
        - key value
        hash: section

        >>> print(result)
        {
            'original': 'https://user:pass@example.com:8080/path?key=value#section',
            'protocol': 'https',
            'username': 'user',
            'password': 'pass',
            'hostname': 'example.com',
            'port': 8080,
            'path': '/path',
            'query': 'key=value',
            'query_params': [('key', 'value')],
            'fragment': 'section'
        }

    """
    parsed: ParseResult = urlparse(url)

    result: dict[str, int | list[tuple[str, str]] | str | None] = {
        "original": url,
        "protocol": parsed.scheme or None,
        "username": parsed.username,
        "password": parsed.password,
        "hostname": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path or None,
        "query": parsed.query or None,
        "query_params": parse_qsl(parsed.query) if parsed.query else [],
        "fragment": parsed.fragment or None,
    }

    return result
