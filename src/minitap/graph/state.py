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
    initial_goal: Annotated[str, "Initial goal given by the user"]
    is_goal_achieved: Annotated[bool, "Whether the goal has been achieved"]
    device_id: Annotated[str, "ID of the device we're interacting with"]
    trace_id: Annotated[str | None, "ID of the run"]
    latest_ui_hierarchy: Annotated[str | None, "Latest UI hierarchy"]
    subgoal_history: Annotated[list[Subgoal], "History of subgoals"]
    current_subgoal: Annotated[Optional[Subgoal], "Current subgoal"]
    memory: Annotated[Optional[str], "Your long term memory"]
