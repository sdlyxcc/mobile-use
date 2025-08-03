from operator import add

from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic
from pydantic import BaseModel
from typing_extensions import Annotated, Optional


class Subgoal(BaseModel):
    description: Annotated[str, "Description of the subgoal"]
    completion_reason: Annotated[
        Optional[str], "Reason why the subgoal was completed (failure or success)"
    ]
    success: bool


class State(AgentStatePydantic):
    # planner related keys
    initial_goal: Annotated[str, "Initial goal given by the user"]

    # orchestrator related keys
    is_goal_achieved: Annotated[bool, "Whether the goal has been achieved"]
    subgoal_history: Annotated[list[Subgoal], "History of subgoals"]

    # contextor related keys
    latest_screenshot_base64: Annotated[str | None, "Latest screenshot of the device"]
    latest_ui_hierarchy: Annotated[Optional[str], "Latest UI hierarchy of the device"]
    focused_app_info: Annotated[Optional[str], "Focused app info"]
    screen_size: Annotated[Optional[str], "Screen size"]
    device_date: Annotated[Optional[str], "Date of the device"]

    # cortex related keys
    structured_decisions: Annotated[
        dict,
        "Structured decisions made by the cortex, for the executor to follow",
    ]

    # common keys
    current_subgoal: Annotated[Optional[Subgoal], "Current subgoal"]
    agents_thoughts: Annotated[
        list[str],
        "All thoughts and reasons that led to actions (why a tool was called, expected outcomes..)",
        add,
    ]
    # extra keys
    trace_id: Annotated[str | None, "ID of the run"]
