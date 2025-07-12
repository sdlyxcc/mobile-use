from langchain_core.messages import HumanMessage, RemoveMessage, ToolMessage
from langchain_mcp_adapters.tools import ImageContent
from minitap.constants import EXPIRED_TOOL_MESSAGE
from minitap.graph.state import State
from minitap.utils.media import compress_base64_jpeg


def handle_screenshot(state: State):
    messages = state.messages
    assert isinstance(messages[-1], ToolMessage)

    last_message: ToolMessage = messages[-1]
    image_artifact: ImageContent = last_message.artifact[0]

    compressed_image_base64 = compress_base64_jpeg(image_artifact.data)

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
    compressed_screenshot_message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{compressed_image_base64}"},
            },
        ]
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

    last_message_id: str = last_message.id  # type: ignore
    return {
        "messages": [
            *expired_screenshot_messages,
            RemoveMessage(id=last_message_id),
            tool_message,
            compressed_screenshot_message,
        ],
    }
