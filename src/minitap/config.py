import logging
from typing import Optional

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from minitap.constants import DEFAULT_MODEL, DEFAULT_PROVIDER
from minitap.context import LLMModel, LLMProvider

load_dotenv(verbose=True)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    LLM_PROVIDER: LLMProvider = DEFAULT_PROVIDER
    LLM_MODEL: LLMModel = DEFAULT_MODEL

    OPENAI_API_KEY: Optional[SecretStr] = None
    GOOGLE_API_KEY: Optional[SecretStr] = None
    XAI_API_KEY: Optional[SecretStr] = None
    OPEN_ROUTER_API_KEY: Optional[SecretStr] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
