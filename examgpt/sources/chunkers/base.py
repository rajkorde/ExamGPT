from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from examgpt.sources.filetypes.base import Source
from examgpt.utils.misc import get_current_time


@dataclass
class TextChunk:
    id: str
    text: str
    page_number: int | None
    last_updated: str = field(default_factory=get_current_time)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(chunk_dict: dict[str, Any]) -> "TextChunk":
        return TextChunk(**chunk_dict)


class Chunker(Protocol):
    def chunk(self, source: Source) -> list[TextChunk]: ...
