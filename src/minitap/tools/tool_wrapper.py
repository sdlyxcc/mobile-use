from typing import Callable

from pydantic import BaseModel


class ToolWrapper(BaseModel):
    name: str
    tool_fn: Callable
    on_success_fn: Callable[..., str]
    on_failure_fn: Callable[..., str]
