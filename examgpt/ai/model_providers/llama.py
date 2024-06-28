from dataclasses import dataclass, field

from langchain_community.chat_models import ChatOllama

from examgpt.ai.base import ModelConfig, ModelProvider
from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.core.config import settings

logger = settings.get_logger()


@dataclass
class LlamaConfig(ModelConfig):
    family: ModelFamily = field(default=ModelFamily.OLLAMA)
    name: ModelName = field(default=ModelName.LLAMA3)
    cost_ppm_token: int = 0
    chunk_size: int = 2500


class LlamaProvider(ModelProvider):
    def __init__(self, model_config: ModelConfig = LlamaConfig()):
        self.model_config = model_config
        self.chat = ChatOllama(model=str(self.model_config.name.value))
        logger.info(
            f"Setting model provider to {model_config.name} from {model_config.family}."
        )

    def get_chat_model(self) -> ChatOllama:
        return self.chat

    def get_model_name(self) -> ModelName:
        return ModelName.DEFAULT
