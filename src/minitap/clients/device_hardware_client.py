from urllib.parse import urljoin

from minitap.servers.device_hardware_bridge import DEVICE_HARDWARE_BRIDGE_PORT
from minitap.utils.requests_utils import get_session_with_curl_logging


class DeviceHardwareClient:
    def __init__(self, host="localhost", port=DEVICE_HARDWARE_BRIDGE_PORT):
        self.base_url = f"http://{host}:{port}"
        self.session = get_session_with_curl_logging()

    def get(self, path: str, **kwargs):
        url = urljoin(self.base_url, f"/api/{path.lstrip('/')}")
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs):
        url = urljoin(self.base_url, f"/api/{path.lstrip('/')}")
        return self.session.post(url, **kwargs)


def get_client():
    return DeviceHardwareClient()
