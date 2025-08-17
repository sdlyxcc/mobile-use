from enum import Enum

from pydantic import BaseModel


class OrchestratorStatus(Enum):
    CONTINUE = "continue"
    RESUME = "resume"
    REPLAN = "replan"


class OrchestratorOutput(BaseModel):
    status: OrchestratorStatus
    reason: str
