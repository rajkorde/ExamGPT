import sys

# from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    OPENAI_API_KEY: str
    TG_BOT_TOKEN: str
    MODEL_FAMILY: str
    MODEL_NAME: str
    log_level: str = "INFO"
    temp_folder: str = "temp"

    class Config:
        env_file = ".env"

    def __post_init__(self):
        self.configure_logging()

    def configure_logging(self):
        logger.remove()
        logger.add(sys.stdout, level=self.log_level.upper())


settings = ApplicationSettings()
