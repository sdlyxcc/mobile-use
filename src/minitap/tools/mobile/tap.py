from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SelectorRequest
from minitap.controllers.mobile_command_controller import tap as tap_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def tap(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    selector_request: SelectorRequest,
    index: Optional[int] = None,
):
    """
    Taps on a selector.
    Index is optional and is used when you have multiple views matching the same selector.
    """
    output = tap_controller(selector_request=selector_request, index=index)
    return Command(
        update={
            "agents_thoughts": [agent_thought],
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=tap_wrapper.on_success_fn(selector_request, index),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


tap_wrapper = ToolWrapper(
    tool_fn=tap,
    on_success_fn=(
        lambda selector_request,
        index: f"Tap on {selector_request} {"at index {index}" if index else ""} is successful."
    ),
    on_failure_fn=(
        lambda selector_request,
        index: f"Failed to tap on {selector_request} {"at index {index}" if index else ""}."
    ),
)
