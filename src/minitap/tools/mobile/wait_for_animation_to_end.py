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
    name="wait_for_animation_to_end",
    tool_fn=wait_for_animation_to_end,
    on_success_fn=lambda: "Animation ended successfully.",
    on_failure_fn=lambda: "Failed to end animation.",
)
