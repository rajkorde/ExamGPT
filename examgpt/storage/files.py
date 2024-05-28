import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from examgpt.storage.base import Storage


@dataclass
class FileStorage(Storage):
    destination_folder: str

    def copy(self, sources: list[str]) -> None:
        for file in sources:
            print(file)
            file_path = Path(file)
            if not file_path.is_file():
                logger.warning(f"File does not exist: {file_path}")
            else:
                shutil.copy2(file_path, self.destination_folder)
                logger.info(f"Copied file: {file_path}")

    def save_to_json(self, data: dict[Any, Any], filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(data, f)

    def __post_init__(self) -> None:
        path = Path(self.destination_folder)
        path.mkdir(parents=True, exist_ok=True)
