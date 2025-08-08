from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing import Optional
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import launch_app as launch_app_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def launch_app(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    package_name: str,
):
    """Launch an application on the device using the package name on Android, bundle id on iOS."""
    output = launch_app_controller(package_name)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=launch_app_wrapper.on_failure_fn(package_name)
        if has_failed
        else launch_app_wrapper.on_success_fn(package_name),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=launch_app_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [
                    tool_message,
                ],
            },
        ),
    )


launch_app_wrapper = ToolWrapper(
    tool_fn=launch_app,
    on_success_fn=lambda package_name: f"App {package_name} launched successfully.",
    on_failure_fn=lambda package_name: f"Failed to launch app {package_name}.",
)
