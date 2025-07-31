from pathlib import Path
from typing import Optional

from jinja2 import Template
from langchain_core.messages import BaseMessage, SystemMessage
from pydantic import BaseModel, Field

from minitap.graph.state import Subgoal
from minitap.services.llm import get_llm, with_fallback
from minitap.utils.decorators import wrap_with_callbacks


class MemoraOutput(BaseModel):
    reason: str | None = Field(
        description="Briefly explain why you updated or restructured the memory,"
        " how this supports the goal or subgoal. If you only cleaned up or restructured"
        " memory without adding new info, set `reason` to None.",
    )
    updated_memory: str | None = Field(
        description="The entire memory updated, including the interesting"
        " data extracted from the input data if relevant",
        default=None,
    )


@wrap_with_callbacks(
    before=lambda: print("🧠 Starting Memora Agent...", end="", flush=True),
    on_success=lambda _: print("✅", flush=True),
    on_failure=lambda _: print("❌", flush=True),
)
async def memora(
    initial_goal: str,
    current_subgoal: Optional[Subgoal] = None,
    subgoals_history: list[Subgoal] = [],
    last_8_messages: list[BaseMessage] = [],
    current_memory: Optional[str] = None,
) -> tuple[str | None, str | None]:
    system_message = Template(
        Path(__file__).parent.joinpath("memora.md").read_text(encoding="utf-8")
    ).render(
        initial_goal=initial_goal,
        subgoals=subgoals_history,
        current_subgoal=current_subgoal,
        last_8_messages=last_8_messages,
        current_memory=current_memory,
    )
    messages: list[BaseMessage] = [
        SystemMessage(content=system_message),
    ]

    llm_main = get_llm(
        override_provider="openrouter",
        override_model="meta-llama/llama-4-scout",
        override_temperature=0,
    )
    llm_fallback = get_llm(
        override_provider="openai",
        override_model="gpt-4.1",
        override_temperature=0,
    )
    structured_llm_main = llm_main.with_structured_output(MemoraOutput)
    structured_llm_fallback = llm_fallback.with_structured_output(MemoraOutput)

    memora_output: MemoraOutput = await with_fallback(
        lambda: structured_llm_main.ainvoke(messages),
        lambda: structured_llm_fallback.ainvoke(messages),
    )  # type: ignore
    return memora_output.reason, memora_output.updated_memory
