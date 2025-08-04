from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import stop_app as stop_app_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def stop_app(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    package_name: Optional[str] = None,
):
    """
    Stops current application if it is running.
    You can also specify the package name of the app to be stopped.
    """
    output = stop_app_controller(package_name=package_name)
    return Command(
        update={
            "agents_thoughts": [agent_thought],
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=stop_app_wrapper.on_success_fn(package_name),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


stop_app_wrapper = ToolWrapper(
    tool_fn=stop_app,
    on_success_fn=lambda package_name: f"App {package_name or 'current'} stopped successfully.",
    on_failure_fn=lambda package_name: f"Failed to stop app {package_name or 'current'}.",
)
