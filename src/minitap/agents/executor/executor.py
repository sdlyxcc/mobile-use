from pathlib import Path
from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.messages.ai import AIMessage
from minitap.context import get_device_context
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.tools.index import EXECUTOR_WRAPPERS_TOOLS, get_tools_from_wrappers
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Executor Agent..."),
    on_success=lambda _: logger.success("Executor Agent"),
    on_failure=lambda _: logger.error("Executor Agent"),
)
async def executor_node(state: State):
    structured_decisions = state.structured_decisions
    if not structured_decisions:
        logger.warning("No structured decisions found.")
        return {
            "agent_thought": ["No structured decisions found, I cannot execute anything."],
        }
    device_context = get_device_context()

    if len(state.executor_messages) > 0 and isinstance(state.executor_messages[-1], AIMessage):
        if len(state.executor_messages[-1].tool_calls) > 0:  # type: ignore
            # A previous tool call raised an uncaught exception while retrigerring the executor
            return {
                "executor_retrigger": False,
                "executor_failed": True,
                "executor_messages": [state.messages[-1]],
            }

    system_message = Template(
        Path(__file__).parent.joinpath("executor.md").read_text(encoding="utf-8")
    ).render(platform=device_context.mobile_platform)
    cortex_last_thought = (
        state.cortex_last_thought if state.cortex_last_thought else state.agents_thoughts[-1]
    )
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=cortex_last_thought),
        HumanMessage(content=structured_decisions),
        *state.executor_messages,
    ]

    llm = get_llm(agent_node="executor").bind_tools(
        tools=get_tools_from_wrappers(EXECUTOR_WRAPPERS_TOOLS),
        tool_choice="auto",
        parallel_tool_calls=False,
    )
    response = await llm.ainvoke(messages)

    return {
        "cortex_last_thought": cortex_last_thought,
        "executor_messages": [response],
        "messages": [response],
    }
