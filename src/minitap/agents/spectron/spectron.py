from pathlib import Path
from typing import Optional

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from minitap.graph.state import Subgoal
from minitap.services.llm import get_llm, with_fallback
from minitap.utils.decorators import wrap_with_callbacks


class SpectronOutput(BaseModel):
    description: str = Field(description="The description of the UI.")


@wrap_with_callbacks(
    before=lambda: print("👁️📱 Analyzing UI..."),
    on_success=lambda _: print("✅"),
    on_failure=lambda _: print("❌"),
)
async def spectron(
    ui_hierarchy: str,
    initial_goal: str,
    current_subgoal: Optional[Subgoal] = None,
    screenshot_message: Optional[HumanMessage] = None,
) -> SpectronOutput:
    spectron_system_message = Template(
        Path(__file__).parent.joinpath("spectron.md").read_text()
    ).render(
        current_subgoal=current_subgoal,
        initial_goal=initial_goal,
    )
    spectron_messages = [
        SystemMessage(content=spectron_system_message),
        HumanMessage(content=ui_hierarchy),
    ]
    if screenshot_message:
        spectron_messages.append(screenshot_message)

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
    structured_llm_main = llm_main.with_structured_output(SpectronOutput)
    structured_llm_fallback = llm_fallback.with_structured_output(SpectronOutput)

    spectron_output: SpectronOutput = await with_fallback(
        lambda: structured_llm_main.ainvoke(spectron_messages),
        lambda: structured_llm_fallback.ainvoke(spectron_messages),
    )  # type: ignore
    return spectron_output
