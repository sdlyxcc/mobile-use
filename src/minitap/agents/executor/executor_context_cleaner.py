from langchain_core.messages.ai import AIMessage
from minitap.graph.state import State
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Executor Context Cleaner..."),
    on_success=lambda _: logger.success("Executor Context Cleaner"),
    on_failure=lambda _: logger.error("Executor Context Cleaner"),
)
async def executor_context_cleaner_node(state: State):
    """Clears the executor context."""
    update: dict = {
        "executor_failed": False,
        "executor_retrigger": False,
    }
    if len(state.executor_messages) > 0 and isinstance(state.executor_messages[-1], AIMessage):
        if len(state.executor_messages[-1].tool_calls) > 0:  # type: ignore
            # A previous tool call raised an uncaught exception -> sanitize the executor messages
            update["executor_messages"] = [state.messages[-1]]
    return update
