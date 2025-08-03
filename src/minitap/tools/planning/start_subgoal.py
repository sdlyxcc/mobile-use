from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.graph.state import State, Subgoal
from minitap.tools.tool_wrapper import ToolWrapper


@tool
async def start_subgoal(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
    description: str,
):
    """
    Call this when you begin working on a new high-level portion of the task.

    Args:
        description: should explain what this subgoal aims to achieve (not the individual
        steps or UI actions like tap, scroll, ...)
    """
    if state.current_subgoal is not None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="You can't start a new subgoal because subgoal "
                        "'{state.current_subgoal.description}' is still in progress...",
                        tool_call_id=tool_call_id,
                    ),
                ],
            },
        )

    print(f"Starting subgoal '{description}'...")
    new_subgoal = Subgoal(
        description=description,
        completion_reason=None,
        success=False,
    )
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=start_subgoal_wrapper.on_success_fn(new_subgoal.description),
                    tool_call_id=tool_call_id,
                ),
            ],
            "current_subgoal": new_subgoal,
        },
    )


start_subgoal_wrapper = ToolWrapper(
    tool_fn=start_subgoal,
    on_success_fn=lambda description: f"Starting goal '{description}'",
    on_failure_fn=lambda description: f"Failed to start goal '{description}'.",
)
