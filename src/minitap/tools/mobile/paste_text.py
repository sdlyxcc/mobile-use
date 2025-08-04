from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import paste_text as paste_text_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def paste_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
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
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=paste_text_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


paste_text_wrapper = ToolWrapper(
    tool_fn=paste_text,
    on_success_fn=lambda: "Text pasted successfully.",
    on_failure_fn=lambda: "Failed to paste text.",
)
