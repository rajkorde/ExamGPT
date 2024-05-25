from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

# from examgpt.sources.chunkers.base import Chunker
from examgpt.sources.chunkers.textchunk import TextChunk


@dataclass
class Source(ABC):
    filename: str
    # chunker: Chunker
    id: str = field(default_factory=lambda: str(uuid4()))
    full_text: str | None = None

    def __post_init__(self):
        file = Path(self.filename).resolve()
        print(file)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        self.location = str(file)

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...


@dataclass
class Sources:
    sources: list[Source] = field(default_factory=list)
