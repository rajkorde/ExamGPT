from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

# Ignoring PylanceReportMissingTypeStubs for codenamize package
from codenamize import codenamize  # type: ignore

from examgpt.sources.filetypes.base import Source
from examgpt.utils.misc import get_current_time


def get_code() -> str:
    code = codenamize(str(uuid4()))
    # ensure no spaces in the generated code
    while " " in code:
        code = codenamize(str(uuid4()))
    return code


@dataclass
class Exam:
    name: str
    exam_id: str = field(default_factory=get_code)
    sources: list[Source] = field(default_factory=list)
    last_updated: str = field(default_factory=get_current_time)
    post_event: bool = False

    #    _source_mapping: ClassVar[dict[str, Any]] = {SourceType.PDF.value: PDFFile}

    def to_dict(self):
        return {
            "name": self.name,
            "exam_id": self.exam_id,
            "last_updated": self.last_updated,
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
