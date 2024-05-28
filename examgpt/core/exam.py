from dataclasses import dataclass, field
from uuid import uuid4

from examgpt.sources.filetypes.base import Source


@dataclass
class Exam:
    name: str
    sources: list[Source] = field(default_factory=list)
    # TODO: Replace with friendly id
    exam_id: str = field(default_factory=lambda: str(uuid4()))
    post_event: bool = False

    def to_dict(self):
        return {
            "name": self.name,
            "exam_id": self.exam_id,
            "sources": [source.to_dict() for source in self.sources],
        }
