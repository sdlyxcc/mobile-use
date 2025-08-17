from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from mobile_use.controllers.mobile_command_controller import SelectorRequest
from mobile_use.controllers.mobile_command_controller import (
    long_press_on as long_press_on_controller,
)
from mobile_use.tools.tool_wrapper import ExecutorMetadata, ToolWrapper
from typing_extensions import Annotated


@tool
def long_press_on(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    selector_request: SelectorRequest,
    index: Optional[int] = None,
):
    """
    Long press on a UI element identified by the given selector.
    An index can be specified to select a specific element if multiple are found.
    """
    output = long_press_on_controller(selector_request=selector_request, index=index)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=long_press_on_wrapper.on_failure_fn()
        if has_failed
        else long_press_on_wrapper.on_success_fn(),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=long_press_on_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


long_press_on_wrapper = ToolWrapper(
    tool_fn=long_press_on,
    on_success_fn=lambda: "Long press on is successful.",
    on_failure_fn=lambda: "Failed to long press on.",
)
