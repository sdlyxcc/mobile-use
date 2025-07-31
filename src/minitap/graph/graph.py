import asyncio
from typing import Literal

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
from minitap.agents.handle_ui_hierarchy import get_ui_hierarchy
from minitap.agents.history_cleanup import history_cleanup
from minitap.agents.memora.memora import memora
from minitap.agents.planner.planner import planner_node
from minitap.agents.spectron.spectron import spectron
from minitap.constants import MAX_MESSAGES_IN_HISTORY
from minitap.graph.state import State
from minitap.tools.index import ALL_TOOLS
from minitap.tools.maestro import get_maestro_tools
from minitap.utils.conversations import (
    is_ai_message,
    is_fast_nonui_tool,
    is_tool_for_name,
    is_tool_message,
)


async def visualizer_node(state: State):
    if not state.messages:
        return {}
    last_message = state.messages[-1]
    if not is_tool_message(last_message):
        return {}
    if is_fast_nonui_tool(last_message):
        print("⏭️ Skipped UI hierarchy refresh.", flush=True)
        return {}

    latest_ui_hierarchy: str | None = None
    screenshot_message: HumanMessage | None = None
    transformed_messages: list[BaseMessage] = []
    await asyncio.sleep(0.5)
    latest_ui_hierarchy = await get_ui_hierarchy(state)

    if is_tool_for_name(last_message, "take_screenshot"):
        if last_message.artifact and len(last_message.artifact) > 0:
            screenshot_handler_output = await handle_screenshot(state)
            screenshot_message = screenshot_handler_output.screenshot_message
            if screenshot_handler_output.messages:
                transformed_messages.extend(screenshot_handler_output.messages)

    if not latest_ui_hierarchy:
        print(
            "❌ Error: Electron could not be called, since no UI hierarchy"
            " or screenshot was provided.",
            flush=True,
        )
        transformed_messages.append(AIMessage(content="I could not analyze the current screen."))
        return {"messages": transformed_messages}

    electron_output = await spectron(
        ui_hierarchy=latest_ui_hierarchy,
        initial_goal=state.initial_goal,
        current_subgoal=state.current_subgoal,
        screenshot_message=screenshot_message,
    )
    transformed_messages.append(
        AIMessage(
            content="Here is the current screen description:\n\n" + electron_output.description
        )
    )
    return {"messages": transformed_messages, "latest_ui_hierarchy": latest_ui_hierarchy}


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

    return {
        **history_cleanup(state),
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

    graph_builder.add_node("visualizer", visualizer_node)
    graph_builder.add_node("memorizer", memorizer_node)
    graph_builder.add_node("messager", messager_node)
    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("summarizer", summarizer)

    graph_builder.add_edge(START, "visualizer")
    graph_builder.add_edge("visualizer", "memorizer")
    graph_builder.add_edge("memorizer", "messager")
    graph_builder.add_edge("messager", "summarizer")
    graph_builder.add_edge("summarizer", "planner")
    graph_builder.add_edge("tools", "visualizer")

    graph_builder.add_conditional_edges(
        "planner",
        follow_up_gate,
        {
            "invoke_tools": "tools",
            "continue": "visualizer",
            "end": END,
        },
    )

    return graph_builder.compile()
