from typing import cast

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from minitap.config import settings
from minitap.context import (
    LLMModel,
    LLMProvider,
    get_llm_context,
)

AVAILABLE_PROVIDERS: list[LLMProvider] = ["openai", "google", "openrouter"]

AVAILABLE_MODELS: dict[LLMProvider, list[LLMModel]] = {
    "openai": ["o3"],
    "google": ["gemini-2.5-pro"],
    "openrouter": [
        "moonshotai/kimi-k2",
        "meta-llama/llama-4-maverick",
        "meta-llama/llama-4-scout",
    ],
}

DEFAULT_PROVIDER: LLMProvider = "openai"
DEFAULT_MODEL: LLMModel = "o3"


def get_google_llm(
    model_name: str = "gemini-2.5-pro",
    temperature: float = 0.7,
) -> ChatGoogleGenerativeAI:
    client = ChatGoogleGenerativeAI(
        model=model_name,
        max_tokens=None,
        temperature=temperature,
        api_key=SecretStr(settings.GOOGLE_API_KEY) if settings.GOOGLE_API_KEY else None,
        max_retries=2,
    )
    return client


def get_openai_llm(
    model_name: str = "o3",
    temperature: float = 1,
) -> ChatOpenAI:
    client = ChatOpenAI(
        model=model_name,
        api_key=SecretStr(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
        temperature=temperature,
    )
    return client


<<<<<<< HEAD
class ChatOpenRouter(ChatOpenAI):
    """ChatOpenAI wrapper preconfigured for the OpenRouter endpoint."""

    def __init__(self, **kwargs):
        super().__init__(base_url="https://openrouter.ai/api/v1", **kwargs)


def get_openrouter_llm(model_name: str, temperature: float = 1):
    client = ChatOpenRouter(
        model=model_name,
        temperature=temperature,
        api_key=SecretStr(settings.OPENROUTER_API_KEY) if settings.OPENROUTER_API_KEY else None,
    )
    return client


def get_llm(temperature: float = 1):
    """Get LLM instance using provider/model from context, settings, or defaults.
    
    This is the single entry point for LLM selection. It automatically:
    1. Checks ContextVar for provider/model (set by CLI or programmatically)
    2. Falls back to environment settings if available
    3. Uses hardcoded defaults as final fallback
    """
    context_provider, context_model = get_llm_context()
    
    # Use context values if available, otherwise fall back to settings/defaults
    provider = cast(LLMProvider, context_provider or (settings.LLM_PROVIDER or DEFAULT_PROVIDER))
    model_name = cast(LLMModel, context_model or (settings.LLM_MODEL or DEFAULT_MODEL))
    
    return _create_llm(provider, model_name, temperature)


def _create_llm(provider: LLMProvider, model_name: LLMModel, temperature: float = 1):
    """Internal function to create LLM instances."""
    if provider == "openai":
        return ChatOpenAI(
            model=model_name,
            api_key=SecretStr(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
            temperature=temperature,
        )
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(settings.GOOGLE_API_KEY) if settings.GOOGLE_API_KEY else None,
            max_tokens=None,
            max_retries=2,
        )
    elif provider == "openrouter":
        return get_openrouter_llm(model_name, temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# Legacy functions for backward compatibility
def get_llm_legacy(provider: LLMProvider, model_name: LLMModel, temperature: float = 1):
    """Legacy function - prefer get_llm()."""
    return _create_llm(provider, model_name, temperature)


def get_default_llm(temperature: float = 1):
    """Legacy function - prefer get_llm()."""
    return get_llm(temperature)
=======
def get_grok_llm() -> ChatOpenAI:
    client = ChatOpenAI(
        model="grok-4",
        openai_api_key=settings.XAI_API_KEY,  # type: ignore[reportGeneralTypeIssues]
        temperature=1,
        base_url="https://api.x.ai/v1",
    )
    return client
>>>>>>> main
