from __future__ import annotations

import random
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Type
from uuid import uuid4

from examgpt.core.config import settings
from examgpt.core.exceptions import NotEnoughInformationInContext
from examgpt.core.question import (
    LongformEnhanced,
    MultipleChoiceEnhanced,
    QACollection,
    Scenario,
)
from examgpt.utils.checkpoint import CheckpointService
from examgpt.utils.misc import get_current_time

if TYPE_CHECKING:
    from examgpt.ai.aimodel import AIModel
    from examgpt.sources.chunkers.base import Chunker, TextChunk

logger = settings.get_logger()


class SourceType(Enum):
    PDF = "PDF"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    UNKNOWN = "UNKNOWN"


class SourceState(Enum):
    INIT = "INIT"
    SOURCE_COPIED = "SOURCE_COPIED"
    CHUNKED = "CHUNKED"
    QAGENERATED = "QAGENERATED"
    READY = "READY"
    ERROR = "ERROR"


class Source(ABC):
    _registry: dict[SourceType, Type[Source]] = {}

    def __init__(
        self,
        location: str,
        chunker: Chunker,
        qa_collection: Optional[QACollection] = None,
        type: SourceType = SourceType.UNKNOWN,
        id: str = str(uuid4()),
        chunks: list[TextChunk] = [],
    ):
        self.location = location
        self.chunker = chunker
        self.type = type

        self.id = id
        self.chunks = chunks
        self.qa_collection = qa_collection
        self.state: SourceState = SourceState.INIT
        self.full_text = None

        file = Path(self.location).resolve()
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        self.location = str(file)

    @classmethod
    def register_subclass(cls, source_type: SourceType):
        def decorator(subclass: Type[Source]) -> Type[Source]:
            cls._registry[source_type] = subclass
            return subclass

        return decorator

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Source:
        source_type = data.get("type")
        if not source_type:
            raise KeyError(f"Key type not present in data: {data}")

        source_type = SourceType[source_type]
        if source_type not in cls._registry:
            raise ValueError(f"Unknown source type: {source_type}")

        return cls._registry[source_type].from_dict(data)

    def update_location(self, new_location: str) -> None:
        """
        Once the storage provided copies/uploads the source, it sets
        the new location
        """
        self.state = SourceState.SOURCE_COPIED
        self.location = new_location

    def limit_chunks(self, n: int = 5) -> None:
        """
        Limits the number of chunks to process for testing
        """
        self.chunks = random.sample(self.chunks, n)

    @CheckpointService.checkpoint
    def _get_longform_qa(
        self,
        id: str,
        chunk: TextChunk,
        model: AIModel,
        exam_name: str,
        scenario: str = Scenario.LONGFORM.value,
    ) -> LongformEnhanced:
        try:
            qa = model.generate_longform_qa(chunk, exam_name)
            qae = LongformEnhanced(
                **qa.dict(), chunk_id=chunk.id, last_updated=get_current_time()
            )
        except NotEnoughInformationInContext as e:
            logger.warning(e.message)
            qae = LongformEnhanced(
                question="",
                answer="",
                chunk_id=chunk.id,
                last_updated=get_current_time(),
            )
        return qae

    @CheckpointService.checkpoint
    def _get_multiplechoice_qa(
        self,
        id: str,
        chunk: TextChunk,
        model: AIModel,
        exam_name: str,
        scenario: str = Scenario.MULTIPLECHOICE.value,
    ) -> MultipleChoiceEnhanced:
        try:
            qa = model.generate_multiplechoice_qa(chunk, exam_name)
            qae = MultipleChoiceEnhanced(
                **qa.dict(), chunk_id=chunk.id, last_updated=get_current_time()
            )
        except NotEnoughInformationInContext as e:
            logger.warning(e.message)
            qae = MultipleChoiceEnhanced(
                question="",
                answer="",
                choices={},
                chunk_id=chunk.id,
                last_updated=get_current_time(),
            )
        return qae

    def get_qa_collection(
        self,
        exam_id: str,
        exam_name: str,
        model: AIModel,
        scenarios: list[Scenario] = [Scenario.LONGFORM, Scenario.MULTIPLECHOICE],
    ) -> QACollection | None:
        if not self.chunks:
            logger.warning("Chunk the document before asking to generate Q&A")
            return None

        args = {}
        args["exam_id"] = exam_id
        args["source_id"] = self.id
        args["exam_name"] = exam_name
        total_chunks = len(self.chunks)

        for scenario in scenarios:
            if scenario == Scenario.LONGFORM:
                longform_qas: list[LongformEnhanced] = []
                for i, chunk in enumerate(self.chunks):
                    logger.info(
                        f"Creating long form QA for chunk {i}/{total_chunks}: {chunk.id}"
                    )
                    qae = self._get_longform_qa(
                        id=chunk.id,
                        chunk=chunk,
                        model=model,
                        exam_name=exam_name,
                        scenario=Scenario.LONGFORM.value,
                    )
                    longform_qas.append(qae)
                args["long_form_qa"] = [q for q in longform_qas if q.question != ""]

            elif scenario == Scenario.MULTIPLECHOICE:
                multiplechoice_qas: list[MultipleChoiceEnhanced] = []
                for i, chunk in enumerate(self.chunks):
                    logger.info(
                        f"Generating long form QA for chunk {i}/{total_chunks}: {chunk.id}"
                    )
                    qae = self._get_multiplechoice_qa(
                        id=chunk.id,
                        chunk=chunk,
                        model=model,
                        exam_name=exam_name,
                        scenario=Scenario.MULTIPLECHOICE.value,
                    )
                    multiplechoice_qas.append(qae)
                args["multiple_choice_qa"] = [
                    q for q in multiplechoice_qas if q.question != ""
                ]
            else:
                raise ValueError(f"Unsupport scenario: {scenario}")

        self.qa_collection = QACollection(**args)
        self.state = SourceState.QAGENERATED
        return self.qa_collection
