from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import SelectorRequest
from minitap.controllers.mobile_command_controller import long_press_on as long_press_on_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def long_press_on(
    tool_call_id: Annotated[str, InjectedToolCallId],
    selector_request: SelectorRequest,
    index: Optional[int] = None,
):
    output = long_press_on_controller(selector_request=selector_request, index=index)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=long_press_on_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


long_press_on_wrapper = ToolWrapper(
    name="long_press_on",
    tool_fn=long_press_on,
    on_success_fn=lambda: "Long press on is successful.",
    on_failure_fn=lambda: "Failed to long press on.",
)
