from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.graph.state import State
from minitap.tools.tool_wrapper import ToolWrapper


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

    if state.current_subgoal is not None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Cannot complete goal while there is a current subgoal.",
                        tool_call_id=tool_call_id,
                    ),
                ],
            },
        )

    print("Goal completed...")

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=complete_goal_wrapper.on_success_fn(reason),
                    tool_call_id=tool_call_id,
                ),
            ],
            "is_goal_achieved": True,
        },
    )


complete_goal_wrapper = ToolWrapper(
    tool_fn=complete_goal,
    on_success_fn=lambda reason: f"Goal completed: {reason}",
    on_failure_fn=lambda reason: f"Failed to complete goal: {reason}",
)
