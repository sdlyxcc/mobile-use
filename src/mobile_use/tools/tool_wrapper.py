from typing import Callable, Optional

from langchain_core.messages import ToolMessage
from pydantic import BaseModel


class ExecutorMetadata(BaseModel):
    retrigger: bool


class ToolWrapper(BaseModel):
    tool_fn: Callable
    on_success_fn: Callable[..., str]
    on_failure_fn: Callable[..., str]

    def handle_executor_state_fields(
        self,
        executor_metadata: Optional[ExecutorMetadata],
        is_failure: bool,
        tool_message: ToolMessage,
        updates: dict,
    ):
        if executor_metadata is None:
            return updates
        updates["executor_retrigger"] = executor_metadata.retrigger
        updates["executor_messages"] = [tool_message]
        updates["executor_failed"] = is_failure
        return updates
