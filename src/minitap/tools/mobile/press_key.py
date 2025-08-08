from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing import Optional
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import Key
from minitap.controllers.mobile_command_controller import press_key as press_key_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def press_key(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    key: Key,
):
    """Press a key on the device."""
    output = press_key_controller(key)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=press_key_wrapper.on_failure_fn(key)
        if has_failed
        else press_key_wrapper.on_success_fn(key),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=press_key_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


press_key_wrapper = ToolWrapper(
    tool_fn=press_key,
    on_success_fn=lambda key: f"Key {key.value} pressed successfully.",
    on_failure_fn=lambda key: f"Failed to press key {key.value}.",
)
