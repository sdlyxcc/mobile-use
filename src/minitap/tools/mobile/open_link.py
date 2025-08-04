from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import open_link as open_link_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def open_link(
    tool_call_id: Annotated[str, InjectedToolCallId],
    url: str,
):
    """
    Open a link on a device (i.e. a deep link).
    """
    output = open_link_controller(url=url)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=open_link_wrapper.on_success_fn(url),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


open_link_wrapper = ToolWrapper(
    tool_fn=open_link,
    on_success_fn=lambda url: f"Link {url} opened successfully.",
    on_failure_fn=lambda: "Failed to open link.",
)
