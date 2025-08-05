import json
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr, ValidationError
from pydantic_settings import BaseSettings

from minitap.context import LLMConfigContext, set_llm_config_context
from minitap.utils.logger import get_logger

### Environment Variables

load_dotenv(verbose=True)
logger = get_logger(__name__)


class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[SecretStr] = None
    GOOGLE_API_KEY: Optional[SecretStr] = None
    XAI_API_KEY: Optional[SecretStr] = None
    OPEN_ROUTER_API_KEY: Optional[SecretStr] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()


### LLM Configuration

LLMProvider = Literal["openai", "google", "openrouter", "xai"]
AgentNode = Literal["planner", "orchestrator", "cortex", "executor"]


class LLM(BaseModel):
    provider: LLMProvider
    model: str

    def __str__(self):
        return f"{self.provider}/{self.model}"


class LLMConfig(BaseModel):
    planner: LLM
    orchestrator: LLM
    cortex: LLM
    executor: LLM

    def __str__(self):
        return f"""
        📃 Planner: {self.planner}
        🎯 Orchestrator: {self.orchestrator}
        🧠 Cortex: {self.cortex}
        🛠️ Executor: {self.executor}
        """

    def __getitem__(self, item: AgentNode) -> LLM:
        return getattr(self, item)


def get_default_llm_config() -> LLMConfig:
    logger.success("Default llm config set")
    try:
        if not os.path.exists("llm.default.jsonc"):
            raise Exception("Default llm config not found")
        with open("llm.default.jsonc", "r") as f:
            default_config_dict = json.load(f)
        return LLMConfig.model_validate(default_config_dict)
    except Exception as e:
        logger.error(f"Failed to load default llm config: {e}. Falling back to hardcoded config")
        return LLMConfig(
            planner=LLM(provider="openai", model="gpt-4.1"),
            orchestrator=LLM(provider="openai", model="o3"),
            cortex=LLM(provider="openai", model="gpt-4.1"),
            executor=LLM(provider="openai", model="gpt-4.1"),
        )


def deep_merge_llm_config(default: LLMConfig, override: dict) -> LLMConfig:
    merged_dict = default.model_dump()

    for key, override_subdict in override.items():
        if key in merged_dict and isinstance(override_subdict, dict):
            merged_dict[key].update(override_subdict)
        else:
            merged_dict[key] = override_subdict

    return LLMConfig.model_validate(merged_dict)


def parse_llm_config() -> LLMConfig:
    if not os.path.exists("llm.override.jsonc"):
        return get_default_llm_config()

    with open("llm.override.jsonc", "r") as f:
        override_config_dict = json.load(f)

    try:
        default_config = get_default_llm_config()
        return deep_merge_llm_config(default_config, override_config_dict)

    except ValidationError as e:
        logger.error(f"Invalid llm config: {e}. Falling back to default config")
        return get_default_llm_config()


def validate_llm_config(llm_config: LLMConfig):
    for agent_node, agent_llm in llm_config.model_dump().items():

        def error_message(api_key_name: str) -> str:
            return f"{agent_node} requires {api_key_name} to be set in .env file."

        match agent_llm.provider:
            case "openai":
                if not settings.OPENAI_API_KEY:
                    raise Exception(error_message("OPENAI_API_KEY"))
            case "google":
                if not settings.GOOGLE_API_KEY:
                    raise Exception(error_message("GOOGLE_API_KEY"))
            case "openrouter":
                if not settings.OPEN_ROUTER_API_KEY:
                    raise Exception(error_message("OPEN_ROUTER_API_KEY"))
            case "xai":
                if not settings.XAI_API_KEY:
                    raise Exception(error_message("XAI_API_KEY"))


def initialize_llm_config() -> LLMConfig:
    llm_config = parse_llm_config()
    validate_llm_config(llm_config)
    set_llm_config_context(LLMConfigContext(llm_config=llm_config))
    return llm_config
