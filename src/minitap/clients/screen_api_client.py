from urllib.parse import urljoin

from minitap.servers.device_screen_api import DEVICE_SCREEN_API_PORT
from minitap.utils.requests_utils import get_session_with_curl_logging


class ScreenApiClient:
    def __init__(self, host="localhost", port=DEVICE_SCREEN_API_PORT):
        self.base_url = f"http://{host}:{port}"
        self.session = get_session_with_curl_logging()

    def get(self, path: str, **kwargs):
        return self.session.get(urljoin(self.base_url, path), **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(urljoin(self.base_url, path), **kwargs)


def get_client():
    return ScreenApiClient()
