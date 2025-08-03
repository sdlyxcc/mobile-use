from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SelectorRequest
from minitap.controllers.mobile_command_controller import (
    copy_text_from as copy_text_from_controller,
)
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def copy_text_from(
    tool_call_id: Annotated[str, InjectedToolCallId],
    selector_request: SelectorRequest,
):
    output = copy_text_from_controller(selector_request=selector_request)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=copy_text_from_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


copy_text_from_wrapper = ToolWrapper(
    name="copy_text_from",
    tool_fn=copy_text_from,
    on_success_fn=lambda: "Text copied successfully.",
    on_failure_fn=lambda: "Failed to copy text.",
)
