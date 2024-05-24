import sys

from loguru import logger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = "INFO"

    def configure_logging(self):
        logger.remove()
        logger.add(sys.stdout, level=self.log_level.upper())
