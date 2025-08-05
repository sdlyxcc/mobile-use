from typing import Optional

from pydantic import BaseModel, Field


class CortexOutput(BaseModel):
    decisions: str = Field(..., description="The decisions to be made. A stringified JSON object")
    agent_thought: str = Field(..., description="The agent's thought")
    complete_current_subgoal: Optional[bool] = Field(
        False, description="Whether the current subgoal is complete"
    )
