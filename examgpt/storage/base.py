from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from examgpt.core.exam import Exam
from examgpt.sources.filetypes.base import Source


class StorageType(Enum):
    FILE = "file"
    CLOUD = "cloud"


class Storage(ABC):
    @abstractmethod
    def copy(self, sources: list[Source]) -> None: ...

    @abstractmethod
    def save_to_json(self, data: dict[Any, Any], filename: str) -> None: ...

    @abstractmethod
    def get_exam(self, location: str) -> Exam: ...
