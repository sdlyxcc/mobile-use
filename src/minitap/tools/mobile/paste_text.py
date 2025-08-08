from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing import Optional
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import paste_text as paste_text_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def paste_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
):
    """
    Pastes text previously copied via `copyTextFrom` into the currently focused field.

    Note:
        The text field must be focused before using this command.

    Example:
        - copyTextFrom: { id: "someId" }
        - tapOn: { id: "searchFieldId" }
        - pasteText
    """
    output = paste_text_controller()
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=paste_text_wrapper.on_failure_fn()
        if has_failed
        else paste_text_wrapper.on_success_fn(),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=paste_text_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


paste_text_wrapper = ToolWrapper(
    tool_fn=paste_text,
    on_success_fn=lambda: "Text pasted successfully.",
    on_failure_fn=lambda: "Failed to paste text.",
)
