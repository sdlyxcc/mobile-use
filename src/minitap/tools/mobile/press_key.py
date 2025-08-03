from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import Key
from minitap.controllers.mobile_command_controller import press_key as press_key_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def press_key(
    tool_call_id: Annotated[str, InjectedToolCallId],
    key: Key,
):
    output = press_key_controller(key)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=press_key_wrapper.on_success_fn(key),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


press_key_wrapper = ToolWrapper(
    name="press_key",
    tool_fn=press_key,
    on_success_fn=lambda key: f"Key {key.value} pressed successfully.",
    on_failure_fn=lambda key: f"Failed to press key {key.value}.",
)
