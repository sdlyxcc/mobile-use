from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import (
    take_screenshot as take_screenshot_controller,
)
from minitap.tools.tool_wrapper import ToolWrapper
from minitap.utils.media import compress_base64_jpeg


@tool
def take_screenshot(
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """
    Take a screenshot of the device.
    """
    output = take_screenshot_controller()
    compressed_image_base64 = compress_base64_jpeg(output)
    return Command(
        update={
            "latest_screenshot_base64": compressed_image_base64,
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=take_screenshot_wrapper.on_success_fn(),
                ),
            ],
        },
    )


take_screenshot_wrapper = ToolWrapper(
    tool_fn=take_screenshot,
    on_success_fn=lambda: "Screenshot taken successfully.",
    on_failure_fn=lambda: "Failed to take screenshot.",
)
