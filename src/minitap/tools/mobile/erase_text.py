from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import erase_text as erase_text_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def erase_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    output = erase_text_controller()
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=erase_text_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


erase_text_wrapper = ToolWrapper(
    tool_fn=erase_text,
    on_success_fn=lambda: "Text erased successfully.",
    on_failure_fn=lambda: "Failed to erase text.",
)
