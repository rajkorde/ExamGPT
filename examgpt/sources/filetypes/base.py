from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from examgpt.sources.chunkers.base import Chunker, TextChunk


class SourceType(Enum):
    PDF = "PDF"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"


@dataclass
class Source(ABC):
    location: str
    type: SourceType
    chunker: Chunker
    chunks: list[TextChunk] = field(default_factory=list)
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @staticmethod
    @abstractmethod
    def from_dict(source_dict: dict[str, Any]) -> Source: ...

    def update_location(self, new_location: str) -> None:
        self.location = new_location
