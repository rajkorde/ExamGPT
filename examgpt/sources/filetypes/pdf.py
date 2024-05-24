import json
import os
from dataclasses import dataclass, field
from typing import Sequence

from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from examgpt.sources.chunkers.textchunk import TextChunk
from examgpt.sources.filetypes.base import Source


@dataclass
class PDFFile(Source):
    _elements: Sequence[Element] = field(default_factory=list)

    chunks: list[TextChunk] = field(default_factory=list)
    chunk_size: int = 2500

    def _split_pdf(self) -> None:
        if not self.location.endswith(".pdf"):
            raise ValueError(f"File is not a PDF: {self.location}")

        self._elements = partition_pdf(
            self.location,
            chunking_strategy="by_title",
            max_characters=2500,
            include_orig_elements=True,
            extract_images_in_pdf=False,
        )

    def chunk(self) -> list[TextChunk]:
        if len(self._elements) == 0:
            self._split_pdf()

        chunks: list[TextChunk] = []
        for element in self._elements:
            id = str(element.id)
            text = element.text
            page_number = element.metadata.page_number
            chunks.append(TextChunk(id, text, page_number))

        self.chunks = chunks
        return chunks

    def create_text(self) -> str:
        if len(self._elements) == 0:
            self._split_pdf()
        self.full_text = "".join([element.text for element in self._elements])
        return self.full_text

    def write_to_json(self, output_file: str) -> None:
        with open(output_file, "w") as f:
            json.dump([chunk.to_dict() for chunk in self.chunks], f)
