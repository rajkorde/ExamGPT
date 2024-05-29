from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

import tiktoken

from examgpt.core.question import LongForm, MultipleChoice

# from pydantic_settings import BaseSettings


class ModelFamily(Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GOOGLE = "google"


class ModelName(Enum):
    GPT3_5_TURBO = "gpt-3.5-turbo-0125"
    GPT4O = "gpt-4o"
    GEMINIPRO1_5 = "geminipro-1.5"
    GEMINI_FLASH = "geminiflash"
    LLAMA2 = "llama2"
    LLAMA3 = "llama3"


@dataclass
class ModelConfig:
    family: ModelFamily
    name: ModelName
    cost_ppm_token: int
    temperature: float = 0.7
    # bump the cost of by this amount to factor in input and output tokens being different price
    fuzz_factor: float = 1.3

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
class OpenAIConfig(ModelConfig):
    family: ModelFamily = field(default=ModelFamily.OPENAI)
    name: ModelName = field(default=ModelName.GPT3_5_TURBO)
    cost_ppm_token: int = 50


class GenerateLongForm(Protocol):
    def generate_lf(self, text: str) -> LongForm: ...


class GenerateLongFormOpenAI(GenerateLongForm):
    def generate_lf(self, text: str) -> LongForm:
        # prompt = "..."
        # chat_completion = "..."
        question = "who am i"
        answer = "super_user"
        lf = LongForm(question=question, answer=answer)
        return lf


class GenerateMultipleChoice(Protocol):
    def generate_mc(self, text: str) -> MultipleChoice: ...


class GenerateMultipleChoiceOpenAI:
    def generate_mc(self, text: str) -> MultipleChoice:
        # prompt = "..."
        # chat_completion = "..."
        question = "who am i"
        answer = "super_user"
        mc = MultipleChoice(
            question=question, answer=answer, choices=["A", "B", "C", "D"]
        )
        return mc


class GenerateAnswer(Protocol):
    def generate_answer(self, text: str) -> str: ...


class GenerateAnswerOpenAI(GenerateAnswer):
    def generate_answer(self, text: str) -> str:
        # prompt = "..."
        # chat_completion = "..."
        answer = "super_user"
        return answer


@dataclass
class ModelFactory(ABC):
    model_config: ModelConfig

    @abstractmethod
    def create_lf_generator(self) -> GenerateLongForm: ...

    @abstractmethod
    def create_mc_generator(self) -> GenerateMultipleChoice: ...

    @abstractmethod
    def create_answer_generator(self) -> GenerateAnswer: ...


@dataclass
class OpenAIFactory(ModelFactory):
    def create_lf_generator(self) -> GenerateLongForm:
        return GenerateLongFormOpenAI()

    def create_mc_generator(self) -> GenerateMultipleChoice:
        return GenerateMultipleChoiceOpenAI()

    def create_answer_generator(self) -> GenerateAnswer:
        return GenerateAnswerOpenAI()


def main():
    model = OpenAIFactory(model_config=OpenAIConfig())
    _ = model.create_lf_generator()
    _ = model.create_mc_generator()
    _ = model.create_answer_generator()
