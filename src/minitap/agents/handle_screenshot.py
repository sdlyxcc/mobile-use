from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    ToolMessage,
)
from pydantic import BaseModel

from minitap.constants import EXPIRED_TOOL_MESSAGE
from minitap.graph.state import State
from minitap.tools.maestro import convert_maestro_screenshot_tool_message_to_human_message
from minitap.utils.conversations import is_tool_message
from minitap.utils.decorators import wrap_with_callbacks


class HandleScreenshotResult(BaseModel):
    messages: list[BaseMessage]
    screenshot_message: HumanMessage


@wrap_with_callbacks(
    before=lambda: print("🖼️ Compressing screenshot...", end="", flush=True),
    on_success=lambda _: print("✅", flush=True),
    on_failure=lambda _: print("❌", flush=True),
    suppress_exceptions=True,
)
async def handle_screenshot(state: State) -> HandleScreenshotResult:
    messages = state.messages
    if not is_tool_message(messages[-1]):
        raise ValueError("Last message is not a tool message")

    last_message: ToolMessage = messages[-1]

    tool_message = ToolMessage(
        tool_call_id=last_message.tool_call_id,
        name=last_message.name,
        content=[
            {
                "type": "text",
                "text": "Screenshot taken",
            },
        ],
    )
    compressed_screenshot_message = convert_maestro_screenshot_tool_message_to_human_message(
        tool_message
    )

    expired_screenshot_messages: list[HumanMessage] = []

    for message in messages[:-1]:
        if isinstance(message, HumanMessage):
            first_content = message.content[0]
            if (
                isinstance(first_content, dict)
                and first_content.get("type") == "image_url"
                and first_content.get("image_url") != EXPIRED_TOOL_MESSAGE
            ):
                message.content = EXPIRED_TOOL_MESSAGE
                expired_screenshot_messages.append(message)

    if not last_message.id:
        raise ValueError("Last message id is None")

    updated_messages = [
        *expired_screenshot_messages,
        RemoveMessage(id=last_message.id),
        tool_message,
        compressed_screenshot_message,
    ]

    return HandleScreenshotResult(
        messages=updated_messages,
        screenshot_message=compressed_screenshot_message,
    )
