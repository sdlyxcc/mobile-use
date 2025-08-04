from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.controllers.mobile_command_controller import run_flow as run_flow_controller
from minitap.tools.tool_wrapper import ToolWrapper


@tool
def run_flow(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    yaml: str,
    dry_run: bool = False,
):
    """
    Run a flow i.e, a sequence of commands.
    """
    output = run_flow_controller(yaml=yaml, dry_run=dry_run)
    return Command(
        update={
            "agents_thoughts": [agent_thought],
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=run_flow_wrapper.on_success_fn(),
                    additional_kwargs={"output": output},
                ),
            ],
        },
    )


run_flow_wrapper = ToolWrapper(
    tool_fn=run_flow,
    on_success_fn=lambda: "Flow run successfully.",
    on_failure_fn=lambda: "Failed to run flow.",
)
