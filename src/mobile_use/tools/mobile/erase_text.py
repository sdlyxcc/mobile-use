from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from mobile_use.controllers.mobile_command_controller import erase_text as erase_text_controller
from mobile_use.tools.tool_wrapper import ExecutorMetadata, ToolWrapper
from typing_extensions import Annotated


@tool
def erase_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
):
    """
    Erases up to `count` characters from the currently selected text field (default: 50).

    iOS Note:
        This may be flaky on iOS. As a workaround:
            - long_press_on("<input id>")
            - tap_on("Select All")
            - erase_text()

    Matches 'clearText' in search.
    """
    output = erase_text_controller()
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=erase_text_wrapper.on_failure_fn()
        if has_failed
        else erase_text_wrapper.on_success_fn(),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=erase_text_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


erase_text_wrapper = ToolWrapper(
    tool_fn=erase_text,
    on_success_fn=lambda: "Text erased successfully.",
    on_failure_fn=lambda: "Failed to erase text.",
)
