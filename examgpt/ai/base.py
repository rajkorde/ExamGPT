from abc import ABC, abstractmethod
from dataclasses import dataclass

import tiktoken
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_random_exponential

from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.core.question import LongForm, MultipleChoice


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


@dataclass
class AIModel(ABC):
    model_config: ModelConfig
    chat: BaseChatModel

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def get_chat_completion(self, messages: list[SystemMessage | HumanMessage]) -> str:
        response = self.chat.invoke(messages)
        return str(response.content)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def get_chat_completion_async(
        self,
        messages: list[SystemMessage | HumanMessage],
    ) -> str:
        response = await self.chat.ainvoke(messages)
        return str(response.content)

    @abstractmethod
    def generate_longform_qa(self, chunk: str, exam_name: str) -> LongForm: ...

    @abstractmethod
    def generate_multiplechoice_qa(self, chunk: str) -> MultipleChoice: ...

    @abstractmethod
    def generate_answer(self, chunk: str, question: str) -> str: ...
