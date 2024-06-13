from dataclasses import dataclass, field
from typing import Any, ClassVar
from uuid import uuid4

# Ignoring PylanceReportMissingTypeStubs for codenamize package
from codenamize import codenamize  # type: ignore

from examgpt.sources.filetypes.base import Source, SourceType
from examgpt.utils.misc import get_current_time

# from examgpt.sources.filetypes.pdf import PDFFile


@dataclass
class Exam:
    name: str
    sources: list[Source] = field(default_factory=list)
    last_updated: str = field(default_factory=get_current_time)
    exam_id: str = field(default_factory=lambda: codenamize(str(uuid4())))
    post_event: bool = False

    #    _source_mapping: ClassVar[dict[str, Any]] = {SourceType.PDF.value: PDFFile}

    def to_dict(self):
        return {
            "name": self.name,
            "exam_id": self.exam_id,
            "created_time": self.last_updated,
            "sources": [source.to_dict() for source in self.sources],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Exam":
        return Exam(
            name=data["name"],
            exam_id=data["exam_id"],
            last_updated=data["last_updated"],
            sources=[Source.from_dict(source) for source in data["sources"]],
        )
