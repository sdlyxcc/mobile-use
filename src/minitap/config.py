import os
from pathlib import Path
from typing import Literal, Optional, cast

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr, ValidationError
from pydantic_settings import BaseSettings

from minitap.utils.file import load_jsonc
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

ROOT_DIR = Path(__file__).parent.parent.parent
DEFAULT_LLM_CONFIG_FILENAME = "llm-config.defaults.jsonc"
OVERRIDE_LLM_CONFIG_FILENAME = "llm-config.override.jsonc"


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
    try:
        if not os.path.exists(ROOT_DIR / DEFAULT_LLM_CONFIG_FILENAME):
            raise Exception("Default llm config not found")
        with open(ROOT_DIR / DEFAULT_LLM_CONFIG_FILENAME, "r") as f:
            default_config_dict = load_jsonc(f)
        return LLMConfig.model_validate(default_config_dict["default"])
    except Exception as e:
        logger.error(f"Failed to load default llm config: {e}. Falling back to hardcoded config")
        return LLMConfig(
            planner=LLM(provider="openai", model="gpt-4.1"),
            orchestrator=LLM(provider="openai", model="gpt-4.1"),
            cortex=LLM(provider="openai", model="o3"),
            executor=LLM(provider="openai", model="gpt-4.1"),
        )


def deep_merge_llm_config(default: LLMConfig, override: dict) -> LLMConfig:
    merged_dict = default.model_dump()

    for key, override_subdict in override.items():
        if key in merged_dict and isinstance(override_subdict, dict):
            for sub_key, sub_value in override_subdict.items():
                if sub_value:
                    merged_dict[key][sub_key] = sub_value
        elif override_subdict:
            merged_dict[key] = override_subdict

    return LLMConfig.model_validate(merged_dict)


def parse_llm_config() -> LLMConfig:
    if not os.path.exists(ROOT_DIR / DEFAULT_LLM_CONFIG_FILENAME):
        return get_default_llm_config()

    override_config_dict = {}
    if os.path.exists(ROOT_DIR / OVERRIDE_LLM_CONFIG_FILENAME):
        logger.info("Loading custom llm config...")
        with open(ROOT_DIR / OVERRIDE_LLM_CONFIG_FILENAME, "r") as f:
            override_config_dict = load_jsonc(f)
    else:
        logger.warning("Custom llm config not found, loading default config")

    try:
        default_config = get_default_llm_config()
        return deep_merge_llm_config(default_config, override_config_dict)

    except ValidationError as e:
        logger.error(f"Invalid llm config: {e}. Falling back to default config")
        return get_default_llm_config()


def validate_llm_config(llm_config: LLMConfig):
    for agent_node, agent_llm in vars(llm_config).items():
        agent_node = cast(AgentNode, agent_node)
        agent_llm = cast(LLM, agent_llm)

        match agent_llm.provider:
            case "openai":
                if not settings.OPENAI_API_KEY:
                    raise Exception(f"{agent_node} requires OPENAI_API_KEY in .env")
            case "google":
                if not settings.GOOGLE_API_KEY:
                    raise Exception(f"{agent_node} requires GOOGLE_API_KEY in .env")
            case "openrouter":
                if not settings.OPEN_ROUTER_API_KEY:
                    raise Exception(f"{agent_node} requires OPEN_ROUTER_API_KEY in .env")
            case "xai":
                if not settings.XAI_API_KEY:
                    raise Exception(f"{agent_node} requires XAI_API_KEY in .env")


def initialize_llm_config() -> LLMConfig:
    llm_config = parse_llm_config()
    validate_llm_config(llm_config)
    logger.success("LLM config initialized")
    return llm_config
