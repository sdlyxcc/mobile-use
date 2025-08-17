from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from mobile_use.controllers.mobile_command_controller import SelectorRequest
from mobile_use.controllers.mobile_command_controller import tap as tap_controller
from mobile_use.tools.tool_wrapper import ExecutorMetadata, ToolWrapper
from typing_extensions import Annotated


@tool
def tap(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    selector_request: SelectorRequest,
    index: Optional[int] = None,
):
    """
    Taps on a selector.
    Index is optional and is used when you have multiple views matching the same selector.
    """
    output = tap_controller(selector_request=selector_request, index=index)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=tap_wrapper.on_failure_fn(selector_request, index)
        if has_failed
        else tap_wrapper.on_success_fn(selector_request, index),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=tap_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


tap_wrapper = ToolWrapper(
    tool_fn=tap,
    on_success_fn=(
        lambda selector_request,
        index: f"Tap on {selector_request} {'at index {index}' if index else ''} is successful."
    ),
    on_failure_fn=(
        lambda selector_request,
        index: f"Failed to tap on {selector_request} {'at index {index}' if index else ''}."
    ),
)
