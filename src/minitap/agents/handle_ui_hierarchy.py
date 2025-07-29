from langchain_core.messages import ToolMessage

from minitap.graph.state import State
from minitap.tools.maestro import invoke_maestro_tool
from minitap.utils.decorators import wrap_with_callbacks


@wrap_with_callbacks(
    before=lambda: print("🔄.. Refreshing UI hierarchy...", end="", flush=True),
    on_success=lambda _: print("✅", flush=True),
    on_failure=lambda _: print("❌", flush=True),
    suppress_exceptions=True,
)
async def get_ui_hierarchy(state: State) -> str | None:
    messages = state.messages
    if not isinstance(messages[-1], ToolMessage):
        raise ValueError(
            "❗❗ WARNING: Last message is not a tool message. Not refreshing UI hierarchy."
        )
    tool_message = await invoke_maestro_tool("inspect_view_hierarchy", state.device_id)

    if not tool_message or not isinstance(tool_message.content, str):
        raise ValueError("Tool message or tool message content is None")

    ui_hierarchy: str = tool_message.content
    return ui_hierarchy
