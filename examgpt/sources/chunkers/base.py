from dataclasses import asdict, dataclass
from typing import Any, Protocol

from examgpt.sources.filetypes.base import Source


@dataclass
class TextChunk:
    id: str
    text: str
    page_number: int | None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(chunk_dict: dict[str, Any]) -> "TextChunk":
        return TextChunk(**chunk_dict)


class Chunker(Protocol):
    def chunk(self, source: Source) -> list[TextChunk]: ...
