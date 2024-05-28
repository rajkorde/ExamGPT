# import json
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

# from typing import Sequence
# from unstructured.documents.elements import Element
# from unstructured.partition.pdf import partition_pdf

if TYPE_CHECKING:
    from examgpt.sources.chunkers.base import TextChunk
from examgpt.sources.filetypes.base import Source


@dataclass
class PDFFile(Source):
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

    # def create_text(self) -> str:
    #     if len(self._elements) == 0:
    #         self._split_pdf()
    #     self.full_text = "".join([element.text for element in self._elements])
    #     return self.full_text

    # def write_to_json(self, output_file: str) -> None:
    #     with open(output_file, "w") as f:
    #         json.dump([chunk.to_dict() for chunk in self.chunks], f)
