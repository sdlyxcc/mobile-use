from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.agents.hopper.hopper import HopperOutput, hopper
from minitap.controllers.platform_specific_commands import list_packages as list_packages_command
from minitap.graph.state import State


@tool
async def list_packages(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
) -> Command:
    """List installed packages on the device."""
    print("Listing packages...")
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
                "messages": [
                    ToolMessage(
                        content="Failed to extract insights from previous task.",
                        tool_call_id=tool_call_id,
                    ),
                ],
            },
        )

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=hopper_output.step + ": " + hopper_output.output,
                    tool_call_id=tool_call_id,
                ),
            ],
        },
    )
