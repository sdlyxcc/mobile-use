import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(verbose=True)


class Settings(BaseSettings):
    GOOGLE_API_KEY: str | None = os.environ.get("GOOGLE_API_KEY")
    OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
    OPENROUTER_API_KEY: str | None = os.environ.get("OPENROUTER_API_KEY")
    XAI_API_KEY: str | None = os.environ.get("XAI_API_KEY")

    LLM_PROVIDER: str | None = os.environ.get("LLM_PROVIDER")
    LLM_MODEL: str | None = os.environ.get("LLM_MODEL")
    LANGCHAIN_API_KEY: str | None = os.environ.get("LANGCHAIN_API_KEY")
    LANGSMITH_TRACING: str | None = os.environ.get("LANGSMITH_TRACING")
    LANGSMITH_ENDPOINT: str | None = os.environ.get("LANGSMITH_ENDPOINT")
    LANGSMITH_PROJECT: str | None = os.environ.get("LANGSMITH_PROJECT")
    model_config = {"env_file": ".env", "extra": "ignore"}


try:
    settings = Settings()
except Exception as e:
    raise ValueError("Missing required environment variables. Please check your .env file.") from e
