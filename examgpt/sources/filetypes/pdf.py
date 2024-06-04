# import json
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from attr import field

# from typing import Sequence
# from unstructured.documents.elements import Element
# from unstructured.partition.pdf import partition_pdf
from examgpt.sources.chunkers.base import TextChunk
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.base import Source, SourceType


@dataclass
class PDFFile(Source):
    type: SourceType = field(default=SourceType.PDF)

    def chunk(self) -> list[TextChunk]:
        self.chunks = self.chunker.chunk(self)
        return self.chunks

    def create_text(self) -> str:
        if self.full_text:
            return self.full_text

        if not self.chunks:
            self.chunks = self.chunker.chunk(self)

        self.full_text = "".join([chunk.text for chunk in self.chunks])
        return self.full_text

    @staticmethod
    def from_dict(source_dict: dict[str, Any]) -> "PDFFile":
        return PDFFile(
            location=source_dict["location"],
            type=SourceType(source_dict["type"]),
            id=source_dict["id"],
            chunks=[TextChunk.from_dict(chunk) for chunk in source_dict["chunks"]],
            chunker=SimplePDFChunker(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "location": self.location,
            "id": self.id,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }
