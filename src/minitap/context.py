"""
Context variables for global state management.

Uses ContextVar to avoid prop drilling and maintain clean function signatures.
"""

from contextvars import ContextVar

from typing_extensions import Literal, Optional

# Type definitions for providers and models
LLMProvider = Literal["openai", "google", "openrouter", "xai"]
LLMModel = Literal[
    # OpenAI models
    "o3",
    "gpt-4.1",
    # Google models
    "gemini-2.5-pro",
    # OpenRouter models
    "moonshotai/kimi-k2",
    "meta-llama/llama-4-maverick",
    "meta-llama/llama-4-scout",
    # XAI models
    "grok-4",
]

# Context variables for LLM configuration
llm_provider_context: ContextVar[Optional[LLMProvider]] = ContextVar("llm_provider", default=None)
llm_model_context: ContextVar[Optional[LLMModel]] = ContextVar("llm_model", default=None)


def set_llm_context(provider: LLMProvider, model: LLMModel) -> None:
    """Set the LLM provider and model in context."""
    llm_provider_context.set(provider)
    llm_model_context.set(model)


def get_llm_context() -> tuple[Optional[LLMProvider], Optional[LLMModel]]:
    """Get the current LLM provider and model from context."""
    return llm_provider_context.get(), llm_model_context.get()


def clear_llm_context() -> None:
    """Clear the LLM context."""
    llm_provider_context.set(None)
    llm_model_context.set(None)
