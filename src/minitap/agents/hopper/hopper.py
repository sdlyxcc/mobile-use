from pathlib import Path
from typing import Sequence, Optional

from jinja2 import Template
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from minitap.services.llm import get_default_llm, get_llm
from pydantic import BaseModel, Field


class HopperOutput(BaseModel):
    step: str = Field(
        description=(
            "The step that has been done, must be a valid one following the "
            "current steps and the current goal to achieve."
        )
    )
    output: str = Field(description="The interesting data extracted from the input data.")


async def hopper(
    initial_goal: str, 
    messages: Sequence[BaseMessage], 
    data: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> HopperOutput:
    print("Starting Hopper Agent", flush=True)
    system_message = Template(Path(__file__).parent.joinpath("hopper.md").read_text()).render(
        initial_goal=initial_goal,
        messages=messages,
    )
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=data),
    ]

    # Use provider/model if specified, otherwise use default
    if provider and model:

        llm = get_llm(provider, model)
    else:

        llm = get_default_llm()
    structured_llm = llm.with_structured_output(HopperOutput)
    response: HopperOutput = await structured_llm.ainvoke(messages)  # type: ignore
    return HopperOutput(
        step=response.step,
        output=response.output,
    )
