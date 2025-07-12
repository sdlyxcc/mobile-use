import uuid

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    StdioConnection,
)
from minitap.constants import FORBIDDEN_MAESTRO_TOOLS, HIDDEN_MAESTRO_TOOLS

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


async def get_view_hierarchy(device_id: str):
    all_maestro_tools = await get_maestro_tools(return_all=True)
    inspect_view_hierarchy_tool: BaseTool | None = None
    for tool in all_maestro_tools:
        if tool.name == "inspect_view_hierarchy":
            inspect_view_hierarchy_tool = tool
            break
    else:
        print(
            "WARNING: inspect_view_hierarchy tool not found."
            " Not returning an up-to-date view hierarchy.."
        )
        return None
    if inspect_view_hierarchy_tool:
        tool_message = await inspect_view_hierarchy_tool.ainvoke(
            {
                "type": "tool_call",
                "args": {
                    "device_id": device_id,
                },
                "id": uuid.uuid4().hex,
            }
        )
        return tool_message.content
