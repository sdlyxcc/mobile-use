import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from minitap.config import settings
from minitap.constants import AVAILABLE_MODELS, DEFAULT_MODEL, DEFAULT_PROVIDER
from minitap.context import (
    LLMModel,
    LLMProvider,
    get_llm_context,
)

logger = logging.getLogger(__name__)


def validate_model_for_provider(provider: LLMProvider, model: LLMModel) -> bool:
    if model not in AVAILABLE_MODELS[provider]:
        logger.warning(
            f"Model '{model}' is not valid for provider '{provider}'. "
            f"Available models: {AVAILABLE_MODELS[provider]}"
        )
        return False
    return True


def get_google_llm(
    model_name: str = "gemini-2.5-pro",
    temperature: float = 0.7,
) -> ChatGoogleGenerativeAI:
    assert settings.GOOGLE_API_KEY is not None
    client = ChatGoogleGenerativeAI(
        model=model_name,
        max_tokens=None,
        temperature=temperature,
        api_key=settings.GOOGLE_API_KEY,
        max_retries=2,
    )
    return client


def get_openai_llm(
    model_name: str = "o3",
    temperature: float = 1,
) -> ChatOpenAI:
    assert settings.OPENAI_API_KEY is not None
    client = ChatOpenAI(
        model=model_name,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )
    return client


def get_openrouter_llm(model_name: str, temperature: float = 1):
    assert settings.OPEN_ROUTER_API_KEY is not None
    client = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.OPEN_ROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    return client


def get_grok_llm(model_name: str, temperature: float = 1) -> ChatOpenAI:
    assert settings.XAI_API_KEY is not None
    client = ChatOpenAI(
        model=model_name,
        api_key=settings.XAI_API_KEY,
        temperature=temperature,
        base_url="https://api.x.ai/v1",
    )
    return client


def get_llm(
    override_provider: Optional[LLMProvider] = None,
    override_model: Optional[LLMModel] = None,
    override_temperature: float = 1,
):
    """Get LLM instance using provider/model from context, environment variables, or defaults.

    This is the single entry point for LLM selection. It automatically:
    1. Checks ContextVar for provider/model (set by CLI or programmatically)
    2. Falls back to environment variables if available
    3. Uses hardcoded defaults as final fallback
    """

    if override_provider and override_model:
        return _create_llm(override_provider, override_model, override_temperature)

    context_provider, context_model = get_llm_context()
    if context_provider and context_model:
        return _create_llm(context_provider, context_model, override_temperature)

    logger.warning("LLM provider or model not found in context. Checking environment variables...")
    if settings.LLM_PROVIDER and settings.LLM_MODEL:
        return _create_llm(settings.LLM_PROVIDER, settings.LLM_MODEL, override_temperature)

    logger.warning(
        "LLM provider or model not found in environment variables."
        "Falling back to {DEFAULT_PROVIDER}/{DEFAULT_MODEL}"
    )
    return _create_llm(DEFAULT_PROVIDER, DEFAULT_MODEL, override_temperature)


def _create_llm(provider: LLMProvider, model_name: LLMModel, temperature: float = 1):
    """Internal function to create LLM instances."""
    if provider == "openai":
        return get_openai_llm(model_name, temperature)
    elif provider == "google":
        return get_google_llm(model_name, temperature)
    elif provider == "openrouter":
        return get_openrouter_llm(model_name, temperature)
    elif provider == "xai":
        return get_grok_llm(model_name, temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
