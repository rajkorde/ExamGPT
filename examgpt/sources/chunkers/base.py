from dataclasses import asdict, dataclass
from typing import Protocol

from examgpt.sources.filetypes.base import Source


@dataclass
class TextChunk:
    id: str
    text: str
    page_number: int | None

    def to_dict(self):
        return asdict(self)


@dataclass
class SourceChunks:
    exam_id: str
    source_id: str
    chunks: list[TextChunk]


class Chunker(Protocol):
    def chunk(self, source: Source) -> list[TextChunk]: ...
