from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from loguru import logger

from examgpt.core.exceptions import (
    NoScenariosProvided,
    NotEnoughInformationInContext,
    UnSupportedScenario,
)
from examgpt.core.question import LongForm, MultipleChoice, QACollection, Scenario

if TYPE_CHECKING:
    from examgpt.ai.aimodel import AIModel
    from examgpt.sources.chunkers.base import Chunker, TextChunk


class SourceType(Enum):
    PDF = "PDF"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"


@dataclass
class Source(ABC):
    location: str
    chunker: Chunker
    type: SourceType
    chunks: list[TextChunk] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    full_text: str | None = None

    def __post_init__(self):
        file = Path(self.location).resolve()
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        self.location = str(file)

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @staticmethod
    @abstractmethod
    def from_dict(source_dict: dict[str, Any]) -> Source: ...

    def update_location(self, new_location: str) -> None:
        self.location = new_location

    def limit_chunks(self, n: int = 5) -> None:
        self.chunks = self.chunks[:n]

    def get_qa_collection(
        self,
        exam_id: str,
        exam_name: str,
        model: AIModel,
        scenarios: list[Scenario] = [Scenario.LONGFORM, Scenario.MULTIPLECHOICE],
    ) -> QACollection | None:
        if not scenarios:
            raise NoScenariosProvided()
        if not self.chunks:
            logger.warning("Chunk the document before asking to generate Q&A")
            return None

        args = {}
        args["exam_id"] = exam_id
        args["source_id"] = self.id

        for scenario in scenarios:
            if scenario == Scenario.LONGFORM:
                longform_qas: list[LongForm] = []
                for chunk in self.chunks:
                    try:
                        qa = model.generate_longform_qa(chunk, exam_name)
                        longform_qas.append(qa)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)

                args["long_form_qa"] = longform_qas
            elif scenario == Scenario.MULTIPLECHOICE:
                multiplechoice_qas: list[MultipleChoice] = []
                for chunk in self.chunks:
                    try:
                        qa = model.generate_multiplechoice_qa(chunk, exam_name)
                        multiplechoice_qas.append(qa)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)
                args["multiple_choice_qa"] = multiplechoice_qas
            else:
                raise UnSupportedScenario(str(scenario))

            return QACollection(**args)
