from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from minitap.servers.device_hardware_bridge import DEVICE_HARDWARE_BRIDGE_PORT
from minitap.utils.logger import get_logger

load_dotenv(verbose=True)
logger = get_logger(__name__)


class ServerSettings(BaseSettings):
    DEVICE_HARDWARE_BRIDGE_BASE_URL: str = f"http://localhost:{DEVICE_HARDWARE_BRIDGE_PORT}"
    DEVICE_SCREEN_API_PORT: int = 9998

    model_config = {"env_file": ".env", "extra": "ignore"}


server_settings = ServerSettings()
