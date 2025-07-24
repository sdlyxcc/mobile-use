from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from minitap.config import settings


AVAILABLE_PROVIDERS = ["openai", "google", "openrouter"]

AVAILABLE_MODELS = {
    "openai": ["o3"],
    "google": ["gemini-2.5-pro"],
    "openrouter": [
        "moonshotai/kimi-k2",
        "meta-llama/llama-4-maverick",
        "meta-llama/llama-4-scout",
    ],
}

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "o3"


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


def get_llm(provider: str, model_name: str, temperature: float = 1):

    
    if provider == "openai":

        client = ChatOpenAI(
            model=model_name,
            api_key=SecretStr(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
            temperature=temperature,
        )
        return client
    if provider == "google":

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(settings.GOOGLE_API_KEY) if settings.GOOGLE_API_KEY else None,
            max_tokens=None,
            max_retries=2,
        )
    if provider == "openrouter":

        return get_openrouter_llm(model_name, temperature)
    raise ValueError(f"Unsupported provider: {provider}")


def get_default_llm():
    provider = settings.LLM_PROVIDER or DEFAULT_PROVIDER
    model_name = settings.LLM_MODEL or DEFAULT_MODEL

    return get_llm(provider, model_name)
