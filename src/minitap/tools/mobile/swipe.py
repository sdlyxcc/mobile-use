from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SwipeRequest
from minitap.controllers.mobile_command_controller import swipe as swipe_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def swipe(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    swipe_request: SwipeRequest,
):
    """
    Swipes on the screen.
    """
    output = swipe_controller(swipe_request=swipe_request)
    return Command(
        update={
            "agents_thoughts": [agent_thought],
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=swipe_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


swipe_wrapper = ToolWrapper(
    tool_fn=swipe,
    on_success_fn=lambda: "Swipe is successful.",
    on_failure_fn=lambda: "Failed to swipe.",
)
