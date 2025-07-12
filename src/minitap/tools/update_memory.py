from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from minitap.graph.state import State
from typing_extensions import Annotated


@tool
async def add_to_memory(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
    memory_item: str,
):
    """
    Persist critical information that directly helps achieve the user's goal.
    This should be used to store **goal-relevant data** discovered during execution,
    especially after inspecting the UI or calling `take_screenshot`. If the screen shows
    information that won't be easily retrievable later but is useful for progressing
    toward the goal, save it here..
    It appends the memory item you specify to the existing one.

    ✅ Use this to remember facts like:
    - "User email is alice@example.com"
    - "Current balance shown: 1,250 EUR"
    - "Confirmation number: #48293"

    ❌ Do NOT use this for generic observations, UI layouts, or speculative hypotheses.
    Only persist data that brings you closer to fulfilling `initial_goal`.

    Args:
        tool_call_id: Internal reference to the tool invocation (do not modify).
        memory_item: A concise, factual, and **goal-aligned** piece of information.

    Returns:
        A confirmation message and the updated memory state.
    """

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="Memory updated successfully ✅",
                    tool_call_id=tool_call_id,
                ),
            ],
            "memory": state.memory + "\n" + memory_item if state.memory else memory_item,
        },
    )
