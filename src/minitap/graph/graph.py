from typing import Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from minitap.agents.contextor.contextor import contextor_node
from minitap.agents.cortex.cortex import cortex_node
from minitap.agents.executor.executor import executor_node
from minitap.agents.memora.memora import memora
from minitap.agents.orchestrator.orchestrator import orchestrator_node
from minitap.agents.planner.planner import planner_node
from minitap.agents.spectron.spectron import spectron
from minitap.agents.summarizer.summarizer import summarizer_node
from minitap.controllers.mobile_command_controller import wait_for_animation_to_end
from minitap.graph.state import State
from minitap.tools.index import EXECUTOR_WRAPPERS_TOOLS, get_tools_from_wrappers
from minitap.utils.conversations import (
    is_ai_message,
    is_tool_message,
)
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


async def visualizer_node(state: State):
    if not state.messages:
        return {}
    last_message = state.messages[-1]
    if not is_tool_message(last_message):
        return {}

    wait_for_animation_to_end()

    electron_output = await spectron(
        initial_goal=state.initial_goal,
        current_subgoal=state.current_subgoal,
    )
    return {
        "messages": [
            AIMessage(
                content="Here is the current screen description:\n\n" + electron_output.description
            )
        ],
    }


async def memorizer_node(state: State):
    if not state.messages:
        return {}
    reason, updated_memory = await memora(
        initial_goal=state.initial_goal,
        current_subgoal=state.current_subgoal,
        subgoals_history=state.subgoal_history,
        last_8_messages=state.messages[-8:],
        current_memory=state.memory,
    )
    if not reason:
        print("🧠➖ Kept memory unchanged.", flush=True)
        return {}
    if updated_memory:
        print("🧠✅ Restructured memory with new information : ", updated_memory, flush=True)
        message = AIMessage(content="🧠✅ Restructured memory with new information.")
        return {"memory": updated_memory, "messages": [message]}
    return {}


async def messager_node(state: State):
    if not state.messages:
        return {}
    last_message = state.messages[-1]
    if is_tool_message(last_message):
        print(f"🔨{last_message.name}{'✅' if last_message.status == 'success' else '❌'}")

    if is_ai_message(last_message):
        if state.is_goal_achieved:
            return {"messages": [HumanMessage(content="Call `complete_goal` to answer me.")]}

    messages: list[BaseMessage] = list(state.messages)
    # If latest 3 messages are AI messages, it probably means the agent is trying to
    # answer to the user without completing the goal first.
    if len(messages) > 3:
        for msg in messages[-3:]:
            if not isinstance(msg, AIMessage):
                break
        else:
            messages.append(HumanMessage(content="Call `complete_goal` to answer me."))

    return {"messages": messages}


def post_orchestrator_gate(
    state: State,
) -> Literal["continue", "replan", "end"]:
    logger.info("Starting post_orchestrator_gate", flush=True)
    return "continue"


def post_cortex_gate(
    state: State,
) -> Literal["continue", "end_subgoal"]:
    logger.info("Starting post_cortex_gate", flush=True)
    return "continue"


def post_executor_gate(
    state: State,
) -> Literal["invoke_tools", "skip"]:
    logger.info("Starting post_executor_gate", flush=True)
    return "invoke_tools"


def excution_test(state: State):
    messages = state.messages
    if not messages:
        return "continue"
    last_message = messages[-1]

    is_goal_achieved = state.is_goal_achieved
    if is_goal_achieved:
        print("👑 GOAL IS ACHIEVED 👑")
        return "end"

    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls and len(tool_calls) > 0:
            print("🔨👁️ Found tool calls:", tool_calls)
            return "invoke_tools"
        else:
            print("🔨❌ No tool calls found")
    return "continue"


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
    graph_builder.add_edge("cortex", "executor")
    graph_builder.add_conditional_edges(
        "executor",
        post_executor_gate,
        {"invoke_tools": "executor_tools", "skip": "summarizer"},
    )
    graph_builder.add_edge("executor_tools", "summarizer")
    graph_builder.add_edge("summarizer", "contextor")

    return graph_builder.compile()
