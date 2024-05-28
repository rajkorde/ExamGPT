from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from examgpt.sources.filetypes.base import Source


@dataclass
class Storage(ABC):
    @abstractmethod
    def copy(self, sources: list[Source]) -> None: ...

    @abstractmethod
    def save_to_json(self, data: dict[Any, Any], filename: str) -> None: ...
