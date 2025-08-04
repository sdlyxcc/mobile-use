from pathlib import Path

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from minitap.context import get_device_context
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.tools.index import EXECUTOR_WRAPPERS_TOOLS, get_tools_from_wrappers
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Executor Agent..."),
    on_success=lambda _: logger.info("Executor Agent ✅"),
    on_failure=lambda _: logger.info("Executor Agent ❌"),
)
async def executor_node(state: State):
    structured_decisions = state.structured_decisions
    if not structured_decisions:
        logger.warning("No structured decisions found.")
        return {
            "agent_thought": ["No structured decisions found, I cannot execute anything."],
        }
    device_context = get_device_context()

    system_message = Template(Path(__file__).parent.joinpath("executor.md").read_text()).render(
        platform=device_context.mobile_platform,
    )
    last_thought = state.agents_thoughts[-1]
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=last_thought),
        HumanMessage(content=structured_decisions),
    ]

    llm = get_llm(
        override_provider="openai", override_model="gpt-4o", override_temperature=0.2
    ).bind_tools(
        tools=get_tools_from_wrappers(EXECUTOR_WRAPPERS_TOOLS),
        tool_choice="auto",
        strict=True,
    )
    response = await llm.ainvoke(messages)

    return {
        "messages": [response],
        "structured_decisions": None,
    }
