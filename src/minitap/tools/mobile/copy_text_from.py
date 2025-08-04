from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from pydantic import Field
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SelectorRequest
from minitap.controllers.mobile_command_controller import (
    copy_text_from as copy_text_from_controller,
)
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def copy_text_from(
    tool_call_id: Annotated[str, InjectedToolCallId],
    selector_request: SelectorRequest = Field(..., description="The selector to copy text from"),
):
    """
    Copies text from a UI element identified by the given selector and stores it in memory.

    The copied text can be:
      - Pasted later using `pasteText`
      - Accessed in JavaScript via `maestro.copiedText`

    Example Usage:
        - launchApp
        - copyTextFrom: { id: "someId" }
        - tapOn: { id: "searchFieldId" }
        - pasteText

    See the Selectors documentation for supported selector types.
    """
    output = copy_text_from_controller(selector_request=selector_request)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=copy_text_from_wrapper.on_success_fn(selector_request),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


copy_text_from_wrapper = ToolWrapper(
    tool_fn=copy_text_from,
    on_success_fn=lambda selector_request: (
        f'Text copied successfully from selector "{selector_request}".'
    ),
    on_failure_fn=lambda selector_request: f"Failed to copy text from selector {selector_request}.",
)
