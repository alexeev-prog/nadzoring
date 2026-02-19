from socket import getservbyport


def get_service_on_port(port: int) -> str:
    try:
        return getservbyport(port)
    except Exception:
        return "Unknown"
