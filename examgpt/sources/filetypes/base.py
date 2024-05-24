import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4

# from examgpt.sources.chunkers.base import Chunker
from examgpt.sources.chunkers.textchunk import TextChunk


@dataclass
class Source(ABC):
    location: str
    # chunker: Chunker
    id: str = field(default_factory=lambda: str(uuid4()))
    full_text: str | None = None

    def __post_init__(self):
        self.location = os.path.abspath(self.location)
        print(self.location)
        if not os.path.exists(self.location):
            raise FileNotFoundError(f"File not found: {self.location}")

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...


@dataclass
class Sources:
    sources: list[Source] = field(default_factory=list)
