from abc import ABC, abstractmethod
from dataclasses import dataclass

import tiktoken
from langchain.chat_models.base import BaseChatModel

from examgpt.ai.constants import ModelFamily, ModelName


@dataclass
class ModelConfig:
    family: ModelFamily
    name: ModelName
    cost_ppm_token: int
    temperature: float = 0.7
    # bump the cost of by this amount to factor in input and output tokens being different price
    fuzz_factor: float = 1.3
    chunk_size: int = 2500

    def estimate_cost(self, token_count: int) -> float:
        return round(
            (token_count * self.fuzz_factor * self.cost_ppm_token) / 1_000_000, 2
        )

    def get_token_count(self, text: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.name.value)
        num_tokens = len(encoding.encode(text))
        return num_tokens


class ModelProvider(ABC):
    model_config: ModelConfig

    def get_model_config(self) -> ModelConfig:
        return self.model_config

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel: ...

    @abstractmethod
    def get_model_name(self) -> ModelName: ...
