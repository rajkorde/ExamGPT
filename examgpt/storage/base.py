from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Storage(ABC):
    @abstractmethod
    def copy(self, source: str, filename: str) -> None: ...

    @abstractmethod
    def save_to_json(self, data: dict, filename: str) -> None: ...
