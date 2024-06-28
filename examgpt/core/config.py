import sys
from typing import Any

from dotenv import load_dotenv

# from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    OPENAI_API_KEY: str
    TG_BOT_TOKEN: str
    MODEL_FAMILY: str
    MODEL_NAME: str
    GOOGLE_API_KEY: str
    log_level: str = Field(default="DEBUG")
    temp_folder: str = Field(default="temp")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        assert load_dotenv()

    # class Config:
    #     env_file = ".env"

    def __post_init__(self):
        self.configure_logging(self.log_level)

    def configure_logging(self, level: str):
        logger.remove()
        logger.add(sys.stdout, level=level.upper())

    def get_logger(self):
        return logger


settings = ApplicationSettings()  # pyright: ignore
