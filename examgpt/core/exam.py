from dataclasses import dataclass, field
from uuid import uuid4

from examgpt.sources.filetypes.base import Sources


@dataclass
class Exam:
    name: str
    sources: Sources
    # TODO: Replace with friendly id
    exam_id: str = field(default_factory=lambda: str(uuid4()))
    post_event: bool = False
