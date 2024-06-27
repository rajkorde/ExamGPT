# import json
from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from examgpt.core.question import QACollection
from examgpt.sources.chunkers.base import Chunker, TextChunk
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.base import Source, SourceState, SourceType


@Source.register_subclass(SourceType.PDF)
class PDFFile(Source):
    def __init__(
        self,
        location: str,
        qa_collection: Optional[QACollection] = None,
        type: SourceType = SourceType.PDF,
        id: str = str(uuid4()),
        chunks: list[TextChunk] = [],
    ):
        super().__init__(location, qa_collection, type, id, chunks)

    def chunk(self, chunker: Chunker = SimplePDFChunker()) -> list[TextChunk]:
        self.chunks = chunker.chunk(self)
        self.state = SourceState.CHUNKED
        return self.chunks

    def create_text(self, chunker: Chunker = SimplePDFChunker()) -> str:
        if self.full_text:
            return self.full_text

        if not self.chunks:
            self.chunks = chunker.chunk(self)

        self.full_text = "".join([chunk.text for chunk in self.chunks])
        return self.full_text

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PDFFile:
        return PDFFile(
            location=data["location"],
            type=SourceType(data["type"]),
            id=data["id"],
            chunks=[TextChunk.from_dict(chunk) for chunk in data["chunks"]],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "location": self.location,
            "id": self.id,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }
