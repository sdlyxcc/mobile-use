from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import input_text as input_text_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def input_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
    text: str,
):
    output = input_text_controller(text=text)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=input_text_wrapper.on_success_fn(text),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


input_text_wrapper = ToolWrapper(
    name="input_text",
    tool_fn=input_text,
    on_success_fn=lambda text: f"Successfully typed {text}",
    on_failure_fn=lambda text: f"Failed to input text {text}",
)
