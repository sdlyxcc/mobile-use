"""
Context variables for global state management.

Uses ContextVar to avoid prop drilling and maintain clean function signatures.
"""

from contextvars import ContextVar

from pydantic import BaseModel
from typing_extensions import Literal, Optional

from minitap.config import LLMConfig, get_default_llm_config


class LLMConfigContext(BaseModel):
    llm_config: LLMConfig


llm_config_context_var: ContextVar[LLMConfigContext] = ContextVar(
    "llm_config_context", default=LLMConfigContext(llm_config=get_default_llm_config())
)


def set_llm_config_context(llm_config_context: LLMConfigContext) -> None:
    llm_config_context_var.set(llm_config_context)


def get_llm_config_context() -> LLMConfigContext:
    return llm_config_context_var.get()


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


def is_execution_setup_set() -> bool:
    return execution_setup.get() is not None


def get_execution_setup() -> ExecutionSetup:
    context = execution_setup.get()
    if context is None:
        raise ValueError("Execution setup is not initialized")
    return context
