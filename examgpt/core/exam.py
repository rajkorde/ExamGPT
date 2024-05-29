from dataclasses import dataclass, field
from typing import Any, ClassVar
from uuid import uuid4

from examgpt.sources.filetypes.base import Source, SourceType
from examgpt.sources.filetypes.pdf import PDFFile


@dataclass
class Exam:
    name: str
    sources: list[Source] = field(default_factory=list)
    # TODO: Replace with friendly id
    exam_id: str = field(default_factory=lambda: str(uuid4()))
    post_event: bool = False

    _source_mapping: ClassVar[dict[str, Any]] = {SourceType.PDF.value: PDFFile}

    def to_dict(self):
        return {
            "name": self.name,
            "exam_id": self.exam_id,
            "sources": [source.to_dict() for source in self.sources],
        }

    @staticmethod
    def from_dict(exam_dict: dict[str, Any]) -> "Exam":
        return Exam(
            name=exam_dict["name"],
            exam_id=exam_dict["exam_id"],
            sources=[
                Exam._source_mapping[source["type"]].from_dict(source)
                for source in exam_dict["sources"]
            ],
        )
