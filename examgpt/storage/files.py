import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from examgpt.core.config import settings
from examgpt.core.exam import Exam
from examgpt.core.question import QACollection
from examgpt.sources.filetypes.base import Source
from examgpt.storage.base import Storage

logger = settings.get_logger()


@dataclass
class FileStorage(Storage):
    folder: str

    def __post_init__(self) -> None:
        path = Path(self.folder)
        path.mkdir(parents=True, exist_ok=True)

    def copy(self, sources: list[Source]) -> None:
        for source in sources:
            file_path = Path(source.location)
            if not file_path.is_file():
                logger.warning(f"File does not exist: {file_path}")
            else:
                destination_file = shutil.copy2(file_path, self.folder)
                source.update_location(new_location=destination_file)
                logger.info(f"Copied file: {file_path}")

    def save_to_json(self, data: dict[Any, Any], filename: str) -> None:
        filename_with_path = f"{self.folder}/{filename}"
        logger.info(f"Saving data to {filename_with_path}")
        with open(filename_with_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_exam(self, location: str) -> Exam:
        filename_with_path = f"{self.folder}/{location}"
        logger.info(f"Getting data from {filename_with_path}")
        with open(filename_with_path, "r") as f:
            data = json.load(f)
        return Exam.from_dict(data)

    def get_qa_collection(self, location: str) -> QACollection:
        filename_with_path = f"{self.folder}/{location}"
        logger.info(f"Getting data from {filename_with_path}")
        with open(filename_with_path, "r") as f:
            data = json.load(f)
        return QACollection.from_dict(data)
