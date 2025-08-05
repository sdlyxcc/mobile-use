"""
LLM Configuration Context for global state management.

This module was created to break circular imports between config.py and context.py.
"""

from contextvars import ContextVar
from typing import Optional

from pydantic import BaseModel

from minitap.config import LLMConfig


class LLMConfigContext(BaseModel):
    llm_config: LLMConfig


llm_config_context_var: ContextVar[Optional[LLMConfigContext]] = ContextVar(
    "llm_config_context", default=None
)


def set_llm_config_context(llm_config_context: LLMConfigContext) -> None:
    llm_config_context_var.set(llm_config_context)


def get_llm_config_context() -> LLMConfigContext:
    context = llm_config_context_var.get()
    if context is None:
        from minitap.config import get_default_llm_config

        default_config = get_default_llm_config()
        context = LLMConfigContext(llm_config=default_config)
        llm_config_context_var.set(context)
    return context
