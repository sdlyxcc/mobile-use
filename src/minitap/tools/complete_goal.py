from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from minitap.graph.state import State
from typing_extensions import Annotated


@tool
async def complete_goal(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
    reason: str = "",
):
    """Complete the goal.

    Args:
        reason: One-line reasoning behind this action.
    """
    print("Goal completed...")

    return Command(
        update={
            "messages": [
                ToolMessage(content=f"Goal completed: {reason}", tool_call_id=tool_call_id),
            ],
            "is_goal_achieved": True,
        },
    )
