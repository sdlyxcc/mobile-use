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
    agent_thought: str,
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
    return Command(
        update={
            "agents_thoughts": [agent_thought],
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
