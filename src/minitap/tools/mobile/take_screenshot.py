from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import (
    take_screenshot as take_screenshot_controller,
)
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def take_screenshot(
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    output = take_screenshot_controller()
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=take_screenshot_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


take_screenshot_wrapper = ToolWrapper(
    tool_fn=take_screenshot,
    on_success_fn=lambda: "Screenshot taken successfully.",
    on_failure_fn=lambda: "Failed to take screenshot.",
)
