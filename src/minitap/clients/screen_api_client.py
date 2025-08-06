from urllib.parse import urljoin

from minitap.utils.requests_utils import get_session_with_curl_logging


class ScreenApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = get_session_with_curl_logging()

    def get(self, path: str, **kwargs):
        return self.session.get(urljoin(self.base_url, path), **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(urljoin(self.base_url, path), **kwargs)


def get_client(base_url: str | None = None):
    if not base_url:
        base_url = "http://localhost:9998"
    return ScreenApiClient(base_url)
