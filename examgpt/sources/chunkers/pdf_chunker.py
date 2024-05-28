from __future__ import annotations

from typing import TYPE_CHECKING

from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from examgpt.sources.chunkers.base import TextChunk

if TYPE_CHECKING:
    from examgpt.sources.filetypes.base import Source


class SimplePDFChunker:
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size
        self._elements: list[Element] = list()

    def _split_pdf(self, location: str) -> list[Element]:
        if not location.endswith(".pdf"):
            raise ValueError(f"File is not a PDF: {location}")

        elements = partition_pdf(
            location,
            chunking_strategy="by_title",
            max_characters=self.chunk_size,
            include_orig_elements=True,
            extract_images_in_pdf=False,
        )

        return elements

    def chunk(self, source: Source) -> list[TextChunk]:
        if not self._elements:
            self._elements = self._split_pdf(source.location)

        chunks: list[TextChunk] = []
        for element in self._elements:
            id = str(element.id)
            text = element.text
            page_number = element.metadata.page_number
            chunks.append(TextChunk(id, text, page_number))

        self.chunks = chunks
        return chunks
