from langchain_core.messages import ToolMessage
from minitap.constants import EXPIRED_TOOL_MESSAGE
from minitap.graph.state import State


def handle_view_hierarchy(state: State):
    messages = state.messages

    expired_view_hierarchy_tool_messages: list[ToolMessage] = []

    for message in messages[:-1]:
        if isinstance(message, ToolMessage):
            if message.name == "inspect_view_hierarchy" and message.content != EXPIRED_TOOL_MESSAGE:
                message.content = EXPIRED_TOOL_MESSAGE
                expired_view_hierarchy_tool_messages.append(message)

    return {
        "messages": expired_view_hierarchy_tool_messages,
    }
