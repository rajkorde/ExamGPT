import sys

from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    log_level: str = "INFO"
    temp_folder: str = "temp"

    class Config:
        env_file = "../../.env"
        env_file_encoding = "utf-8"

    def __post_init__(self):
        self.configure_logging()
        load_dotenv()

    def configure_logging(self):
        logger.remove()
        logger.add(sys.stdout, level=self.log_level.upper())
