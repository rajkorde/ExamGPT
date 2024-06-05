import sys

# from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    OPENAI_API_KEY: str
    TG_BOT_TOKEN: str
    MODEL_FAMILY: str
    MODEL_NAME: str
    GOOGLE_API_KEY: str
    log_level: str = Field(default="INFO")
    temp_folder: str = Field(default="temp")

    class Config:
        env_file = ".env"

    def __post_init__(self):
        self.configure_logging()

    def configure_logging(self):
        logger.remove()
        logger.add(sys.stdout, level=self.log_level.upper())
