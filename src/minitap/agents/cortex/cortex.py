from pathlib import Path

from jinja2 import Template
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from minitap.agents.cortex.types import CortexOutput
from minitap.agents.planner.utils import get_current_subgoal
from minitap.context import get_device_context
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.utils.conversations import get_screenshot_message_for_llm
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Cortex Agent..."),
    on_success=lambda _: logger.info("Cortex Agent ✅"),
    on_failure=lambda _: logger.info("Cortex Agent ❌"),
)
async def cortex_node(state: State):
    device_context = get_device_context()

    system_message = Template(Path(__file__).parent.joinpath("cortex.md").read_text()).render(
        platform=device_context.mobile_platform,
        initial_goal=state.initial_goal,
        subgoal_plan=state.subgoal_plan,
        current_subgoal=get_current_subgoal(state.subgoal_plan),
        agents_thoughts=state.agents_thoughts,
    )
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(
            content="Here are my device info:\n"
            + device_context.to_str()
            + f"Device date: {state.device_date}\n"
            if state.device_date
            else "" + f"Focused app info: {state.focused_app_info}\n"
            if state.focused_app_info
            else ""
        ),
    ]
    for thought in state.agents_thoughts:
        messages.append(AIMessage(content=thought))

    if state.latest_screenshot_base64:
        messages.append(get_screenshot_message_for_llm(state.latest_screenshot_base64))

    if state.latest_ui_hierarchy:
        messages.append(
            HumanMessage(content="Here is the UI hierarchy:\n" + state.latest_ui_hierarchy)
        )

    llm = get_llm(override_provider="openai", override_model="o3", override_temperature=0.2)
    llm = llm.with_structured_output(CortexOutput)
    response: CortexOutput = await llm.ainvoke(messages)  # type: ignore

    return {
        "agent_thought": [response.agent_thought],
        "structured_decisions": response.decisions if response.complete_current_subgoal else None,
        "latest_screenshot_base64": None,
        "latest_ui_hierarchy": None,
        "focused_app_info": None,
        "device_date": None,
    }
