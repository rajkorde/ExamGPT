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

    # _elements: Sequence[Element] = field(default_factory=list)
    # chunks: list[TextChunk] = field(default_factory=list)
    # chunk_size: int = 2500

    # def _split_pdf(self) -> None:
    #     if not self.location.endswith(".pdf"):
    #         raise ValueError(f"File is not a PDF: {self.location}")

    #     self._elements = partition_pdf(
    #         self.location,
    #         chunking_strategy="by_title",
    #         max_characters=2500,
    #         include_orig_elements=True,
    #         extract_images_in_pdf=False,
    #     )

    # def chunk(self) -> list[TextChunk]:
    #     if len(self._elements) == 0:
    #         self._split_pdf()

    #     chunks: list[TextChunk] = []
    #     for element in self._elements:
    #         id = str(element.id)
    #         text = element.text
    #         page_number = element.metadata.page_number
    #         chunks.append(TextChunk(id, text, page_number))

    #     self.chunks = chunks
    #     return chunks

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

    # def create_text(self) -> str:
    #     if len(self._elements) == 0:
    #         self._split_pdf()
    #     self.full_text = "".join([element.text for element in self._elements])
    #     return self.full_text

    # def write_to_json(self, output_file: str) -> None:
    #     with open(output_file, "w") as f:
    #         json.dump([chunk.to_dict() for chunk in self.chunks], f)
