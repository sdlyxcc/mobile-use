from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.agents.hopper.hopper import HopperOutput, hopper
from minitap.controllers.platform_specific_commands_controller import (
    list_packages as list_packages_command,
)
from minitap.graph.state import State
from minitap.tools.tool_wrapper import ToolWrapper


@tool
async def list_packages(
    tool_call_id: Annotated[str, InjectedToolCallId],
    agent_thought: str,
    state: Annotated[State, InjectedState],
) -> Command:
    """
    Lists all the applications on the device.
    Outputs the full package names list (android) or bundle ids list (IOS).
    """
    output: str = list_packages_command()

    try:
        hopper_output: HopperOutput = await hopper(
            initial_goal=state.initial_goal,
            messages=state.messages,
            data=output,
        )
    except Exception as e:
        print("Failed to extract insights from data: " + str(e))
        return Command(
            update={
                "agents_thoughts": [agent_thought],
                "messages": [
                    ToolMessage(
                        content=list_packages_wrapper.on_failure_fn(),
                        tool_call_id=tool_call_id,
                        additional_kwargs={"output": output},
                    ),
                ],
            },
        )

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=list_packages_wrapper.on_success_fn()
                    + ": "
                    + hopper_output.step
                    + ": "
                    + hopper_output.output,
                    tool_call_id=tool_call_id,
                ),
            ],
        },
    )


list_packages_wrapper = ToolWrapper(
    tool_fn=list_packages,
    on_success_fn=lambda: "Packages listed successfully.",
    on_failure_fn=lambda: "Failed to list packages.",
)
