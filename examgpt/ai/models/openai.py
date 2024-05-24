from .base import ModelConfig, ModelFamily, ModelName


class OpenAIConfig(ModelConfig):
    def __init__(self):
        self.family = ModelFamily.OPENAI
        self.name = ModelName.GPT3_5_TURBO
        self.cost_ppm_token: int = 50
