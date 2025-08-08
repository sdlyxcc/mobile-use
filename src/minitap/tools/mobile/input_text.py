from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing import Optional
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import input_text as input_text_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def input_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    text: str,
):
    """
    Inputs the specified text into the UI (works even if no field is focused).

    Example:
        - inputText: "Hello World"

    Notes:
    - Unicode not supported on Android.

    Random Input Options:
        - inputRandomEmail
        - inputRandomPersonName
        - inputRandomNumber (with optional 'length', default 8)
        - inputRandomText (with optional 'length', default 8)

    Tip:
        Use `copyTextFrom` to reuse generated inputs in later steps.
    """
    output = input_text_controller(text=text)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=input_text_wrapper.on_failure_fn(text)
        if has_failed
        else input_text_wrapper.on_success_fn(text),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=input_text_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


input_text_wrapper = ToolWrapper(
    tool_fn=input_text,
    on_success_fn=lambda text: f"Successfully typed {text}",
    on_failure_fn=lambda text: f"Failed to input text {text}",
)
