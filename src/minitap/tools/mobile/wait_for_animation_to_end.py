from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import WaitTimeout
from minitap.controllers.mobile_command_controller import (
    wait_for_animation_to_end as wait_for_animation_to_end_controller,
)
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def wait_for_animation_to_end(
    tool_call_id: Annotated[str, InjectedToolCallId],
    timeout: Optional[WaitTimeout],
):
    """
    Waits for ongoing animations or videos to finish before continuing.

    If a `timeout` (in milliseconds) is set, the command proceeds after the timeout even if
    the animation hasn't ended.
    The flow continues immediately once the animation is detected as complete.

    Example:
        - waitForAnimationToEnd
        - waitForAnimationToEnd: { timeout: 5000 }
    """
    output = wait_for_animation_to_end_controller(timeout=timeout)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=wait_for_animation_to_end_wrapper.on_success_fn(timeout),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


wait_for_animation_to_end_wrapper = ToolWrapper(
    tool_fn=wait_for_animation_to_end,
    on_success_fn=lambda: "Animation ended successfully.",
    on_failure_fn=lambda: "Failed to end animation.",
)
