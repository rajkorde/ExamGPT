from typing import Protocol

from examgpt.sources.chunkers.textchunk import TextChunk
from examgpt.sources.filetypes.base import Source


class Chunker(Protocol):
    def chunk(self, source: Source) -> list[TextChunk]: ...
