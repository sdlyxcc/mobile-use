from langchain_core.messages import (
    HumanMessage,
    RemoveMessage,
    ToolMessage,
)

from minitap.constants import MAX_MESSAGES_IN_HISTORY
from minitap.graph.state import State


def summarizer_node(state: State):
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
