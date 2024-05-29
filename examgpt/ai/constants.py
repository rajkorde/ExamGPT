from enum import Enum


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
