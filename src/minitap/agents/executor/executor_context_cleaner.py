from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from minitap.graph.state import State
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Executor Context Cleaner..."),
    on_success=lambda _: logger.success("Executor Context Cleaner"),
    on_failure=lambda _: logger.error("Executor Context Cleaner"),
)
async def executor_context_cleaner_node(_: State):
    """Clears the executor context."""
    return {
        "cortex_last_thought": None,
        "executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "executor_failed": False,
        "executor_retrigger": False,
        "structured_decisions": None,
    }
