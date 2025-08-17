from typing import Literal

from langchain_core.messages import (
    AIMessage,
)
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from mobile_use.agents.contextor.contextor import contextor_node
from mobile_use.agents.cortex.cortex import cortex_node
from mobile_use.agents.executor.executor import executor_node
from mobile_use.agents.executor.executor_context_cleaner import executor_context_cleaner_node
from mobile_use.agents.orchestrator.orchestrator import orchestrator_node
from mobile_use.agents.planner.planner import planner_node
from mobile_use.agents.planner.utils import (
    all_completed,
    get_current_subgoal,
    one_of_them_is_failure,
)
from mobile_use.agents.summarizer.summarizer import summarizer_node
from mobile_use.graph.state import State
from mobile_use.tools.index import EXECUTOR_WRAPPERS_TOOLS, get_tools_from_wrappers
from mobile_use.utils.logger import get_logger

logger = get_logger(__name__)


def post_orchestrator_gate(
    state: State,
) -> Literal["continue", "replan", "end"]:
    logger.info("Starting post_orchestrator_gate")
    if one_of_them_is_failure(state.subgoal_plan):
        logger.info("One of the subgoals is in failure state, asking to replan")
        return "replan"

    if all_completed(state.subgoal_plan):
        logger.info("All subgoals are completed, ending the goal")
        return "end"

    if not get_current_subgoal(state.subgoal_plan):
        logger.info("No subgoal running, ending the goal")
        return "end"

    logger.info("Goal is not achieved, continuing")
    return "continue"


def post_cortex_gate(
    state: State,
) -> Literal["continue", "end_subgoal"]:
    logger.info("Starting post_cortex_gate")
    if not state.structured_decisions:
        return "end_subgoal"
    return "continue"


def post_executor_gate(
    state: State,
) -> Literal["invoke_tools", "skip"]:
    logger.info("Starting post_executor_gate")
    messages = state.messages
    if not messages:
        return "skip"
    last_message = messages[-1]

    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls and len(tool_calls) > 0:
            logger.info("🔨👁️  Found tool calls: " + str(tool_calls))
            return "invoke_tools"
        else:
            logger.info("🔨❌ No tool calls found")
    return "skip"


def post_executor_tools_gate(
    state: State,
) -> Literal["continue", "failed", "done"]:
    logger.info("Starting post_executor_tools_gate")
    if state.executor_failed:
        return "failed"
    if state.executor_retrigger:
        return "continue"
    return "done"


async def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(State)

    ## Define nodes
    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("orchestrator", orchestrator_node)

    graph_builder.add_node("contextor", contextor_node)

    graph_builder.add_node("cortex", cortex_node)

    graph_builder.add_node("executor", executor_node)
    executor_tool_node = ToolNode(get_tools_from_wrappers(EXECUTOR_WRAPPERS_TOOLS))
    graph_builder.add_node("executor_tools", executor_tool_node)

    graph_builder.add_node("executor_context_cleaner", executor_context_cleaner_node)
    graph_builder.add_node("summarizer", summarizer_node)

    # Linking nodes
    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "orchestrator")
    graph_builder.add_conditional_edges(
        "orchestrator",
        post_orchestrator_gate,
        {
            "continue": "contextor",
            "replan": "planner",
            "end": END,
        },
    )
    graph_builder.add_edge("contextor", "cortex")
    graph_builder.add_conditional_edges(
        "cortex",
        post_cortex_gate,
        {
            "continue": "executor",
            "end_subgoal": "orchestrator",
        },
    )
    graph_builder.add_conditional_edges(
        "executor",
        post_executor_gate,
        {"invoke_tools": "executor_tools", "skip": "executor_context_cleaner"},
    )
    graph_builder.add_conditional_edges(
        "executor_tools",
        post_executor_tools_gate,
        {
            "continue": "executor",
            "done": "executor_context_cleaner",
            "failed": "executor_context_cleaner",
        },
    )
    graph_builder.add_edge("executor_context_cleaner", "summarizer")
    graph_builder.add_edge("summarizer", "contextor")

    return graph_builder.compile()
