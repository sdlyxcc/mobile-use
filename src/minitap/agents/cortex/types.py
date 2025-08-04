from typing import Optional

from pydantic import BaseModel


class CortexOutput(BaseModel):
    decisions: str
    agent_thought: str
    complete_current_subgoal: Optional[bool] = False
