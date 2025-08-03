from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SelectorRequest
from minitap.controllers.mobile_command_controller import tap as tap_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def tap(
    tool_call_id: Annotated[str, InjectedToolCallId],
    selector_request: SelectorRequest,
    index: Optional[int] = None,
):
    output = tap_controller(selector_request=selector_request, index=index)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=tap_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


tap_wrapper = ToolWrapper(
    name="tap",
    tool_fn=tap,
    on_success_fn=lambda: "Tap is successful.",
    on_failure_fn=lambda: "Failed to tap.",
)
