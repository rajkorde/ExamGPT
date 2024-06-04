from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI

from examgpt.ai.base import ModelConfig, ModelProvider
from examgpt.ai.constants import ModelFamily, ModelName


@dataclass
class GeminiFlashConfig(ModelConfig):
    family: ModelFamily = field(default=ModelFamily.GOOGLE)
    name: ModelName = field(default=ModelName.GEMINI_FLASH)
    cost_ppm_token: int = 36
    chunk_size: int = 2500


class GeminiFlashProvider(ModelProvider):
    def __init__(self, model_config: ModelConfig = GeminiFlashConfig()):
        raise NotImplementedError()

    def get_chat_model(self) -> ChatGoogleGenerativeAI:
        raise NotImplementedError()

    def get_model_name(self) -> ModelName:
        return ModelName.DEFAULT
