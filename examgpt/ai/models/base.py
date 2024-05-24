from abc import ABC
from dataclasses import dataclass
from enum import Enum

import tiktoken

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
