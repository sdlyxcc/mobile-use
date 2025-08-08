from typing import Optional
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import back as back_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def back(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
):
    """Navigates to the previous screen. (Only works on Android for the moment)"""
    output = back_controller()
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=back_wrapper.on_failure_fn() if has_failed else back_wrapper.on_success_fn(),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=back_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


back_wrapper = ToolWrapper(
    tool_fn=back,
    on_success_fn=lambda: "Navigated to the previous screen.",
    on_failure_fn=lambda: "Failed to navigate to the previous screen.",
)
