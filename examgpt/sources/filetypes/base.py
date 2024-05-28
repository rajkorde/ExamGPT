from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from examgpt.sources.chunkers.base import Chunker, TextChunk


@dataclass
class Source(ABC):
    location: str
    chunker: Chunker
    id: str = field(default_factory=lambda: str(uuid4()))
    full_text: str | None = None

    def __post_init__(self):
        file = Path(self.location).resolve()
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        self.location = str(file)

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...

    def update_location(self, new_location: str) -> None:
        self.location = new_location


@dataclass
class Sources:
    sources: list[Source] = field(default_factory=list)

    def to_list(self) -> list[str]:
        return [source.location for source in self.sources]
