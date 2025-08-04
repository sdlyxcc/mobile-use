"""
Context variables for global state management.

Uses ContextVar to avoid prop drilling and maintain clean function signatures.
"""

from contextvars import ContextVar

from pydantic import BaseModel
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


class DeviceContext(BaseModel):
    host_platform: Literal["WINDOWS", "LINUX"]
    mobile_platform: Literal["ANDROID", "IOS"]
    device_id: str
    device_width: int
    device_height: int

    def set(self):
        device_context.set(self)

    def to_str(self):
        return (
            f"Host platform: {self.host_platform}\n"
            f"Mobile platform: {self.mobile_platform}\n"
            f"Device ID: {self.device_id}\n"
            f"Device width: {self.device_width}\n"
            f"Device height: {self.device_height}\n"
        )


device_context: ContextVar[Optional[DeviceContext]] = ContextVar("device_context", default=None)


def get_device_context() -> DeviceContext:
    context = device_context.get()
    if context is None:
        raise ValueError("Device context is not initialized")
    return context


# only contains the trace id for now. may contain other things later
class ExecutionSetup(BaseModel):
    trace_id: str


execution_setup: ContextVar[Optional[ExecutionSetup]] = ContextVar("execution_setup", default=None)


def set_execution_setup(trace_id: str):
    execution_setup.set(ExecutionSetup(trace_id=trace_id))


def get_execution_setup() -> ExecutionSetup:
    context = execution_setup.get()
    if context is None:
        raise ValueError("Execution setup is not initialized")
    return context
