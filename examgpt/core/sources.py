from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Source(ABC):
    location: str
    id: str = field(default_factory=lambda: str(uuid4()))

    @abstractmethod
    def chunk(self) -> None: ...


class PDFFile(Source):
    def chunk(self) -> None:
        pass


@dataclass
class Sources:
    sources: list[Source] = field(default_factory=list)
