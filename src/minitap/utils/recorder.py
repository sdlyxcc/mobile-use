import base64
import time
from pathlib import Path

from langchain_core.messages import BaseMessage

from minitap.context import get_execution_setup
from minitap.controllers.mobile_command_controller import take_screenshot
from minitap.utils.media import compress_base64_jpeg


def record_interaction(response: BaseMessage):
    screenshot_base64 = take_screenshot()
    compressed_screenshot_base64 = compress_base64_jpeg(screenshot_base64, 20)
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
        ) as f:
            f.write(response.model_dump_json())
    except Exception as e:
        print(f"Error recording interaction: {e}")
    return "Screenshot recorded successfully"
