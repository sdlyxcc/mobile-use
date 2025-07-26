from minitap.context import LLMModel, LLMProvider

EXPIRED_TOOL_MESSAGE = "(expired message, removed to save memory)"
FORBIDDEN_MAESTRO_TOOLS = {
    "start_device",
    "list_devices",
    "run_flow_files",
    "query_docs",
    "cheat_sheet",
}
FAST_NON_UI_TOOLS = {
    "update_memory",
    "list_packages",
    "start_subgoal",
    "end_subgoal",
    "complete_goal",
    "take_screenshot",
}
HIDDEN_MAESTRO_TOOLS = {"inspect_view_hierarchy"}
SCREENSHOT_LIFETIME = 3
RECURSION_LIMIT = 400
MAX_MESSAGES_IN_HISTORY = 25

AVAILABLE_MODELS: dict[LLMProvider, list[LLMModel]] = {
    "openai": ["o3"],
    "google": ["gemini-2.5-pro"],
    "openrouter": [
        "moonshotai/kimi-k2",
        "meta-llama/llama-4-maverick",
        "meta-llama/llama-4-scout",
    ],
    "xai": ["grok-4"],
}

DEFAULT_PROVIDER: LLMProvider = "openai"
DEFAULT_MODEL: LLMModel = "o3"
