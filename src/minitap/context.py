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
llm_model_context: ContextVar[Optional[str]] = ContextVar("llm_model", default=None)


def set_llm_context(provider: LLMProvider, model: str) -> None:
    """Set the LLM provider and model in context."""
    llm_provider_context.set(provider)
    llm_model_context.set(model)


def get_llm_context() -> tuple[Optional[LLMProvider], Optional[str]]:
    """Get the current LLM provider and model from context."""
    return llm_provider_context.get(), llm_model_context.get()


def clear_llm_context() -> None:
    """Clear the LLM context."""
    llm_provider_context.set(None)
    llm_model_context.set(None)


class DeviceContext:
    def __init__(
        self,
        host_platform: Literal["WINDOWS", "MACOS", "LINUX"],
        mobile_platform: Literal["ANDROID", "IOS"],
        device_id: str,
        device_width: int,
        device_height: int,
    ):
        self.host_platform = host_platform
        self.mobile_platform = mobile_platform
        self.device_id = device_id
        self.device_width = device_width
        self.device_height = device_height
        device_context.set(self)

    def __str__(self):
        return (
            f"Host platform: {self.host_platform}\n"
            f"Mobile platform: {self.mobile_platform}\n"
            f"Device ID: {self.device_id}\n"
            f"Device width: {self.device_width}\n"
            f"Device height: {self.device_height}\n"
        )


device_context: ContextVar[Optional[DeviceContext]] = ContextVar("device_context", default=None)


def get_device_context() -> Optional[DeviceContext]:
    return device_context.get()
