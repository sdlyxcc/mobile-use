from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import stop_app as stop_app_controller
from minitap.tools.tool_wrapper import ExecutorMetadata, ToolWrapper


@tool
def stop_app(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    executor_metadata: Optional[ExecutorMetadata],
    package_name: Optional[str] = None,
):
    """
    Stops current application if it is running.
    You can also specify the package name of the app to be stopped.
    """
    output = stop_app_controller(package_name=package_name)
    has_failed = output is not None
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=stop_app_wrapper.on_failure_fn(package_name)
        if has_failed
        else stop_app_wrapper.on_success_fn(package_name),
        additional_kwargs={"error": output} if has_failed else {},
    )
    return Command(
        update=stop_app_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


stop_app_wrapper = ToolWrapper(
    tool_fn=stop_app,
    on_success_fn=lambda package_name: f"App {package_name or 'current'} stopped successfully.",
    on_failure_fn=lambda package_name: f"Failed to stop app {package_name or 'current'}.",
)
