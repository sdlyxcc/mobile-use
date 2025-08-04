from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import launch_app as launch_app_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def launch_app(
    tool_call_id: Annotated[str, InjectedToolCallId],
    package_name: str,
):
    """Launch an application on the device using the package name on Android, bundle id on iOS."""
    output = launch_app_controller(package_name)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=launch_app_wrapper.on_success_fn(package_name),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


launch_app_wrapper = ToolWrapper(
    tool_fn=launch_app,
    on_success_fn=lambda package_name: f"App {package_name} launched successfully.",
    on_failure_fn=lambda package_name: f"Failed to launch app {package_name}.",
)
