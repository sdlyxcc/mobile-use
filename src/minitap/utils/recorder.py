import base64
import time
from pathlib import Path

from langchain_core.messages import BaseMessage

from minitap.context import get_execution_setup
from minitap.controllers.mobile_command_controller import take_screenshot
from minitap.utils.logger import get_logger
from minitap.utils.media import compress_base64_jpeg

logger = get_logger(__name__)


def record_interaction(response: BaseMessage):
    logger.info("Recording interaction")
    screenshot_base64 = take_screenshot()
    logger.info("Screenshot taken")
    try:
        compressed_screenshot_base64 = compress_base64_jpeg(screenshot_base64, 20)
    except Exception as e:
        logger.error(f"Error compressing screenshot: {e}")
        return "Could not record this interaction"
    timestamp = time.time()
    folder = (
        Path(__file__).parent.joinpath(f"../../traces/{get_execution_setup().trace_id}").resolve()
    )
    folder.mkdir(parents=True, exist_ok=True)
    try:
        with open(
            folder.joinpath(f"{int(timestamp)}.jpeg").resolve(),
            "wb",
        ) as f:
            f.write(base64.b64decode(compressed_screenshot_base64))

        with open(
            folder.joinpath(f"{int(timestamp)}.json").resolve(),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(response.model_dump_json())
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
    return "Screenshot recorded successfully"
