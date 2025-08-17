from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from mobile_use.controllers.mobile_command_controller import run_flow as run_flow_controller
from mobile_use.tools.tool_wrapper import ToolWrapper
from typing_extensions import Annotated


@tool
def run_flow(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    flow_steps: list,
    dry_run: bool = False,
):
    """
    Run a flow i.e, a sequence of commands.
    """
    output = run_flow_controller(flow_steps=flow_steps, dry_run=dry_run)
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
