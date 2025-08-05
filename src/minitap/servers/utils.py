import psutil

from minitap.servers.device_hardware_bridge import DEVICE_HARDWARE_BRIDGE_PORT
from minitap.servers.device_screen_api import DEVICE_SCREEN_API_PORT


def are_ports_available():
    ports = [DEVICE_SCREEN_API_PORT, DEVICE_HARDWARE_BRIDGE_PORT]
    used_ports = set()

    for conn in psutil.net_connections():
        if conn.status == psutil.CONN_LISTEN and conn.laddr:
            if hasattr(conn.laddr, "port"):
                used_ports.add(conn.laddr.port)
            elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                used_ports.add(conn.laddr[1])

    unavailable_ports = [port for port in ports if port in used_ports]

    return len(unavailable_ports) == 0
