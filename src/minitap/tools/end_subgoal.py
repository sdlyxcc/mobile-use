from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from minitap.agents.judge.judge import JudgeOutput, judge
from minitap.graph.state import State


@tool
async def end_subgoal(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
    succeeded: bool,
    completion_reason: str,
):
    """
    Call this when the current subgoal is either:
        - fully completed (with a CONCISE summary reason - 1 phrase)
        - unreachable (with a reason for failure and what was tried)

    Args:
        succeeded: whether the goal was completed successfully
        completion_reason: concise summary reason (if success) or reason for failure (if failure)
    """
    subgoal = state.current_subgoal
    if subgoal is None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="There is no current subgoal...",
                        tool_call_id=tool_call_id,
                    ),
                ],
            },
        )

    if state.latest_ui_hierarchy is None:
        subgoal.success = succeeded
        subgoal.completion_reason = completion_reason
        state.subgoal_history.append(subgoal)
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Goal '{subgoal.description}' ended.",
                        tool_call_id=tool_call_id,
                    ),
                ],
                "subgoal_history": state.subgoal_history,
                "current_subgoal": None,
            },
        )

    if succeeded:
        judge_output: JudgeOutput = await judge(
            device_id=state.device_id,
            subgoal=subgoal,
            subgoal_history=state.subgoal_history,
            ui_hierarchy=state.latest_ui_hierarchy,
        )
        if judge_output.status == "NO":
            subgoal.success = False
            subgoal.completion_reason = judge_output.reason
            state.subgoal_history.append(subgoal)
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=f"Goal '{subgoal.description}' ended with failure."
                            "Reason: {judge_output.reason}",
                            tool_call_id=tool_call_id,
                        ),
                    ],
                    "subgoal_history": state.subgoal_history,
                    "current_subgoal": None,
                },
            )

    subgoal.success = succeeded
    subgoal.completion_reason = completion_reason
    state.subgoal_history.append(subgoal)

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Goal '{subgoal.description}' ended.",
                    tool_call_id=tool_call_id,
                ),
            ],
            "subgoal_history": state.subgoal_history,
            "current_subgoal": None,
        },
    )
