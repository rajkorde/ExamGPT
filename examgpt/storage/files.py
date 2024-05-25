import json
from pathlib import Path
from typing import Any

from examgpt.storage.base import Storage


class FileStorage(Storage):
    folder: str

    def copy(self, source: str, filename: str) -> None: ...

    def save_to_json(self, data: dict[Any, Any], filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(data, f)

    def __post_init__(self) -> None:
        path = Path(self.folder)
        path.mkdir(parents=True, exist_ok=True)
