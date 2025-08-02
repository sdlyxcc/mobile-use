import base64
import time
from pathlib import Path

from langchain_core.messages import BaseMessage

from minitap.controllers.mobile_command_controller import take_screenshot
from minitap.utils.media import compress_base64_jpeg


def record_interaction(trace_id: str, response: BaseMessage):
    # screenshot: ToolMessage | None = await screenshot_tool.ainvoke(
    #     {
    #         "type": "tool_call",
    #         "args": {
    #             "device_id": device_id,
    #         },
    #         "id": uuid.uuid4().hex,
    #     }
    # )
    # if not screenshot:
    #     return "No screenshot found"

    # screenshot_artifacts: list[ImageContent] = screenshot.artifact
    # if not screenshot_artifacts:
    #     return "No screenshot artifacts found"

    # screenshot_base64 = screenshot_artifacts[0].da    ta

    screenshot_base64 = take_screenshot()
    compressed_screenshot_base64 = compress_base64_jpeg(screenshot_base64, 20)
    timestamp = time.time()
    folder = Path(__file__).parent.joinpath(f"../../traces/{trace_id}").resolve()
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
