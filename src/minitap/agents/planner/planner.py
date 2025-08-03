from pathlib import Path

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from minitap.context import get_device_context
from minitap.controllers.platform_specific_commands import (
    get_date,
    get_focused_app_info,
    get_screen_size,
)
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.tools.index import ALL_TOOLS
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger
from minitap.utils.recorder import record_interaction

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Planner Agent...", end="", flush=True),
    on_success=lambda _: logger.info("Planner Agent ✅", flush=True),
    on_failure=lambda _: logger.info("Planner Agent ❌", flush=True),
)
async def planner_node(state: State):
    device_context = get_device_context()

    system_message = Template(Path(__file__).parent.joinpath("planner.md").read_text()).render(
        initial_goal=state.initial_goal,
        device_id=device_context.device_id,
        focused_app_info=get_focused_app_info(),
        screensize=get_screen_size(),
        subgoal_history=state.subgoal_history,
        current_subgoal=state.current_subgoal,
        device_date=get_date(),
        memory=state.memory,
        observations=state.observations,
    )
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=state.initial_goal),
    ]

    llm = get_llm().bind_tools(
        tools=ALL_TOOLS,
        tool_choice="auto",
    )
    response = await llm.ainvoke(messages)
    logger.info("Response from planner: " + str(response.content))

    if state.trace_id:
        record_interaction(
            trace_id=state.trace_id,
            response=response,
        )

    return {
        "messages": [response],
    }
