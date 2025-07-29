import uuid

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    StdioConnection,
)
from mcp.types import ImageContent

from minitap.constants import FORBIDDEN_MAESTRO_TOOLS, HIDDEN_MAESTRO_TOOLS
from minitap.utils.media import compress_base64_jpeg

_all_maestro_tools = None
_model_maestro_tools = None


async def get_maestro_tools(return_all: bool = True):
    global _model_maestro_tools
    global _all_maestro_tools

    if return_all and _all_maestro_tools:
        return _all_maestro_tools

    if _model_maestro_tools:
        return _model_maestro_tools

    maestro_connection: StdioConnection = {
        "transport": "stdio",
        "command": "maestro",
        "args": ["mcp"],
        "env": None,
        "cwd": None,
        "encoding": "utf-8",
        "encoding_error_handler": "strict",
        "session_kwargs": None,
    }
    client = MultiServerMCPClient({"maestro": maestro_connection})
    maestro_tools = await client.get_tools()

    excluded_tools = FORBIDDEN_MAESTRO_TOOLS
    if not return_all:
        excluded_tools = excluded_tools.union(HIDDEN_MAESTRO_TOOLS)

    maestro_tools = [tool for tool in maestro_tools if tool.name not in excluded_tools]
    if return_all:
        _all_maestro_tools = maestro_tools
    else:
        _model_maestro_tools = maestro_tools
    return maestro_tools


async def invoke_maestro_tool(tool_name: str, device_id: str) -> ToolMessage | None:
    maestro_tools = await get_maestro_tools(return_all=True)
    for tool in maestro_tools:
        if tool.name == tool_name:
            return await tool.ainvoke(
                {
                    "type": "tool_call",
                    "args": {
                        "device_id": device_id,
                    },
                    "id": uuid.uuid4().hex,
                }
            )
    return None


def convert_maestro_screenshot_tool_message_to_human_message(
    tool_message: ToolMessage,
) -> HumanMessage:
    image_artifact: ImageContent = tool_message.artifact[0]
    compressed_image_base64 = compress_base64_jpeg(image_artifact.data)
    return HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{compressed_image_base64}"},
            }
        ]
    )
