from typing import Union

from langchain_core.messages import AIMessage
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic
from typing_extensions import Annotated, Optional

from minitap.agents.planner.types import Subgoal
from minitap.utils.logger import get_logger
from minitap.utils.recorder import record_interaction

logger = get_logger(__name__)


def add_agent_thought(a: list[str], b: Union[str, list[str]]) -> list[str]:
    logger.debug(f"New agent thought: {b}")
    record_interaction(response=AIMessage(content=str(b)))
    if isinstance(b, str):
        return a + [b]
    elif isinstance(b, list):
        return a + b
    raise TypeError("b must be a str or list[str]")


class State(AgentStatePydantic):
    # planner related keys
    initial_goal: Annotated[str, "Initial goal given by the user"]

    # orchestrator related keys
    subgoal_plan: Annotated[list[Subgoal], "The current plan, made of subgoals"]

    # contextor related keys
    latest_screenshot_base64: Annotated[Optional[str], "Latest screenshot of the device"]
    latest_ui_hierarchy: Annotated[Optional[str], "Latest UI hierarchy of the device"]
    focused_app_info: Annotated[Optional[str], "Focused app info"]
    device_date: Annotated[Optional[str], "Date of the device"]

    # cortex related keys
    structured_decisions: Annotated[
        Optional[str],
        "Structured decisions made by the cortex, for the executor to follow",
    ]

    # common keys
    agents_thoughts: Annotated[
        list[str],
        "All thoughts and reasons that led to actions (why a tool was called, expected outcomes..)",
        add_agent_thought,
    ]
