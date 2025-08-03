from langchain_core.messages import AIMessage

from minitap.graph.state import State
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Contextor Agent...", end="", flush=True),
    on_success=lambda _: logger.info("Contextor Agent ✅", flush=True),
    on_failure=lambda _: logger.info("Contextor Agent ❌", flush=True),
)
def contextor_node(state: State):
    return {
        "messages": [
            AIMessage(content="Contextor Agent ✅"),
        ],
    }
