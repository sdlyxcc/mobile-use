import logging
from typing import Awaitable, Callable, Optional, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from minitap.config import LLM, AgentNode, settings
from minitap.context import (
    get_llm_config_context,
)

logger = logging.getLogger(__name__)


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
    agent_node: Optional[AgentNode] = None,
    override_llm: Optional[LLM] = None,
    temperature: float = 1,
):
    if agent_node is None and override_llm is None:
        raise ValueError("Either agent_node or override_llm must be provided")
    llm: LLM | None = override_llm
    if not llm:
        if agent_node is None:
            raise ValueError("Agent node must be provided")
        llm_config = get_llm_config_context().llm_config
        llm = llm_config[agent_node]

    if llm.provider == "openai":
        return get_openai_llm(llm.model, temperature)
    elif llm.provider == "google":
        return get_google_llm(llm.model, temperature)
    elif llm.provider == "openrouter":
        return get_openrouter_llm(llm.model, temperature)
    elif llm.provider == "xai":
        return get_grok_llm(llm.model, temperature)
    else:
        raise ValueError(f"Unsupported provider: {llm.provider}")


T = TypeVar("T")


async def with_fallback(
    main_call: Callable[[], Awaitable[T]], fallback_call: Callable[[], Awaitable[T]]
) -> T:
    try:
        return await main_call()
    except Exception as e:
        print(f"❗ Main LLM inference failed: {e}. Falling back...")
        return await fallback_call()
