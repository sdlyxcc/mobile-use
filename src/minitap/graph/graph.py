import asyncio
from typing import Literal, Optional, Sequence

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    ToolMessage,
)
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from minitap.agents.handle_screenshot import handle_screenshot
from minitap.agents.history_cleanup import history_cleanup
from minitap.agents.orchestrator.orchestrator import orchestrator
from minitap.constants import FAST_NON_UI_TOOLS, MAX_MESSAGES_IN_HISTORY
from minitap.graph.state import State
from minitap.tools.index import ALL_TOOLS
from minitap.tools.maestro import get_maestro_tools, get_view_hierarchy


async def pre_model_hook(state: State):
    skip_ui_hierarchy_refresh = False
    if len(state.messages) > 0:
        last_message = state.messages[-1]
        if isinstance(last_message, ToolMessage):
            if last_message.name in FAST_NON_UI_TOOLS:
                skip_ui_hierarchy_refresh = True

    latest_ui_hierarchy: Optional[str] = None
    if not skip_ui_hierarchy_refresh:
        print("🔄.. Refreshing UI hierarchy...", end="", flush=True)
        await asyncio.sleep(0.5)
        latest_ui_hierarchy = await get_view_hierarchy(device_id=state.device_id)
        print("✅", flush=True)
    else:
        print("⏭️ Skipped UI hierarchy refresh.", flush=True)

    if not state.messages:
        return {}

    transformed_messages: Sequence[BaseMessage] = []
    last_message = state.messages[-1]

    if isinstance(last_message, ToolMessage):
        print(f"🔨{last_message.name}{'✅' if last_message.status == 'success' else '❌'}")
        if last_message.name == "take_screenshot":
            print("🖼️ Compressing screenshot..")
            if last_message.artifact and len(last_message.artifact) > 0:
                transformed_messages = handle_screenshot(state)["messages"]

    # If latest 3 messages are AI messages, it probably means the agent is trying to
    # answer to the user without completing the goal first.
    if len(state.messages) > 3:
        for msg in state.messages[-3:]:
            if not isinstance(msg, AIMessage):
                break
        else:
            transformed_messages.append(HumanMessage(content="Call `complete_goal` to answer me."))

    return {
        **history_cleanup(state, transformed_messages),
        "latest_ui_hierarchy": latest_ui_hierarchy or state.latest_ui_hierarchy,
    }


def follow_up_gate(
    state: State,
) -> Literal["invoke_tools", "continue", "end"]:
    print("Starting follow_up_gate", flush=True)

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
            # for tool_call in tool_calls:
            #     tool_call = cast(ToolCall, tool_call)
            #     if tool_call. == "run_flow":
            #         # get thought_process that is an argument of the tool call
            #         thought_process = tool_call.args.get("thought_process")
            #         flow_yaml = tool_call.args.get("flow_yaml")
            #         if thought_process and flow_yaml:
            #             print(
            #                 "🔨⚡ Thought process and flow_yaml arguments found, ensuring maestro"
            #                 " flow is valid..."
            #             )
            #             return "invoke_tools"  # sanitize_maestro_flow(flow_yaml=flow_yaml,
            #             thought_process=thought_process, subgoal=state.current_subgoal,
            #             ui_hierarchy=state.latest_ui_hierarchy)
            return "invoke_tools"
        else:
            print("🔨❌ No tool calls found")
    return "continue"


def summarizer(state: State):
    if len(state.messages) <= MAX_MESSAGES_IN_HISTORY:
        return {}

    nb_removal_candidates = len(state.messages) - MAX_MESSAGES_IN_HISTORY

    remove_messages = []
    start_removal = False

    for msg in reversed(state.messages[:nb_removal_candidates]):
        if isinstance(msg, (ToolMessage, HumanMessage)):
            start_removal = True
        if start_removal and msg.id:
            remove_messages.append(RemoveMessage(id=msg.id))
    return {
        "messages": remove_messages,
    }


async def get_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(State)

    tools = ALL_TOOLS
    maestro_tools = await get_maestro_tools()
    tool_node = ToolNode(tools + maestro_tools)

    graph_builder.add_node("pre_model_hook", pre_model_hook)
    graph_builder.add_node("orchestrator", orchestrator)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("summarizer", summarizer)

    graph_builder.add_edge(START, "pre_model_hook")
    graph_builder.add_edge("tools", "pre_model_hook")
    graph_builder.add_edge("pre_model_hook", "summarizer")
    graph_builder.add_edge("summarizer", "orchestrator")

    graph_builder.add_conditional_edges(
        "orchestrator",
        follow_up_gate,
        {
            "invoke_tools": "tools",
            "continue": "pre_model_hook",
            "end": END,
        },
    )

    return graph_builder.compile()
