import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from examgpt.sources.filetypes.base import Source
from examgpt.storage.base import Storage


@dataclass
class FileStorage(Storage):
    folder: str

    def copy(self, sources: list[Source]) -> None:
        for source in sources:
            print(source.location)
            file_path = Path(source.location)
            if not file_path.is_file():
                logger.warning(f"File does not exist: {file_path}")
            else:
                destination_file = shutil.copy2(file_path, self.folder)
                source.update_location(new_location=destination_file)
                logger.info(f"Copied file: {file_path}")

    def save_to_json(self, data: dict[Any, Any], filename: str) -> None:
        filename_with_path = f"{self.folder}/{filename}"
        logger.info(f"Saving chunks to {filename_with_path}")
        with open(filename_with_path, "w") as f:
            json.dump(data, f, indent=4)

    def __post_init__(self) -> None:
        path = Path(self.folder)
        path.mkdir(parents=True, exist_ok=True)
