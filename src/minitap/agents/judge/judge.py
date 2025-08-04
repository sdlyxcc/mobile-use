from pathlib import Path
from typing import Literal

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from minitap.controllers.mobile_command_controller import take_screenshot
from minitap.graph.state import Subgoal
from minitap.services.llm import get_llm, with_fallback
from minitap.utils.conversations import get_screenshot_message_for_llm


class ScreenshotBasedJudgeOutput(BaseModel):
    status: Literal["OK", "NO"] = Field(
        description=("The status of the subgoal, must be one of 'OK' or 'NO'.")
    )
    reason: str = Field(description="The reason for the status.")


class JudgeOutput(BaseModel):
    status: Literal["OK", "NO", "NEED_SCREENSHOT"] = Field(
        description=("The status of the subgoal, must be one of 'OK', 'NO', or 'NEED_SCREENSHOT'.")
    )
    reason: str = Field(description="The reason for the status.")


async def judge(
    device_id: str,
    subgoal: Subgoal,
    subgoal_history: list[Subgoal],
    ui_hierarchy: str,
) -> JudgeOutput:
    print("Starting Judge Agent", flush=True)
    judge_system_message = Template(Path(__file__).parent.joinpath("judge.md").read_text()).render(
        subgoal=subgoal,
        subgoal_history=subgoal_history,
    )
    judge_messages = [
        SystemMessage(content=judge_system_message),
        HumanMessage(content=ui_hierarchy),
    ]

    screenshot_verifier_system_message = Template(
        Path(__file__).parent.joinpath("screenshot_based_judge.md").read_text()
    ).render(
        subgoal=subgoal,
        subgoal_history=subgoal_history,
    )
    screenshot_verifier_messages = [
        SystemMessage(content=screenshot_verifier_system_message),
        HumanMessage(content=ui_hierarchy),
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
    structured_llm_main = llm_main.with_structured_output(JudgeOutput)
    structured_llm_fallback = llm_fallback.with_structured_output(JudgeOutput)

    judge_output: JudgeOutput = await with_fallback(
        lambda: structured_llm_main.ainvoke(judge_messages),
        lambda: structured_llm_fallback.ainvoke(judge_messages),
    )  # type: ignore

    if judge_output.status == "NEED_SCREENSHOT":
        print(
            "🖼️❔ Need screenshot to verify subgoal completion. " "Reason: ",
            judge_output.reason,
            flush=True,
        )
        screenshot_base64 = take_screenshot()
        screenshot_human_message = get_screenshot_message_for_llm(screenshot_base64)
        screenshot_verifier_messages.append(screenshot_human_message)

        screenshot_verifier_output: ScreenshotBasedJudgeOutput = await with_fallback(
            lambda: structured_llm_main.ainvoke(screenshot_verifier_messages),
            lambda: structured_llm_fallback.ainvoke(screenshot_verifier_messages),
        )  # type: ignore

        print("Screenshot verifier output:", screenshot_verifier_output, flush=True)

        if screenshot_verifier_output.status == "OK":
            return JudgeOutput(status="OK", reason=screenshot_verifier_output.reason)
        elif screenshot_verifier_output.status == "NO":
            return JudgeOutput(status="NO", reason=screenshot_verifier_output.reason)

    print("✅ Subgoal verified.", flush=True)
    print("Judge output:", judge_output, flush=True)
    return judge_output
