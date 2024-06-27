from pathlib import Path
from typing import Optional

from rich import print
from tenacity import retry, stop_after_attempt

from examgpt.ai.aimodel import AIModel
from examgpt.core.config import settings
from examgpt.core.exam import Exam
from examgpt.core.question import QACollection
from examgpt.sources.chunkers.base import Chunker
from examgpt.sources.filetypes.base import Source
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.base import Storage
from examgpt.utils.checkpoint import CheckpointService

logger = settings.get_logger()


@retry(stop=stop_after_attempt(10))
def get_qa_collection(
    source: Source, exam_id: str, exam_name: str, model: AIModel
) -> QACollection | None:
    qa_collection = source.get_qa_collection(exam_id, exam_name, model)
    return qa_collection


class CLIHelper:
    def __init__(
        self,
        name: str,
        location: str,
        code: Optional[str],
    ):
        self.name = name
        self.location = location
        if code:
            self.code = code

    def initialize(self) -> str:
        self.source = PDFFile(location=self.location)
        logger.info(self.source.to_dict())
        self.exam = (
            Exam(name=self.name, sources=[self.source], exam_id=self.code)
            if self.code
            else Exam(name=self.name, sources=[self.source])
        )
        self.code = self.exam.exam_id
        logger.info(self.exam)
        return self.exam.exam_id

    def set_storage(self, storage: Storage):
        self.storage = storage

    def copy(self):
        self.storage.copy(sources=self.exam.sources)
        logger.info(f"New content location: {self.source.location}")

    def chunk(self, chunker: Chunker):
        self.source.chunk(chunker)
        self.storage.save_to_json(data=self.exam.to_dict(), filename="chunks.json")

    def generate_qa(self, model: AIModel, limit: Optional[int]):
        if limit:
            self.source.limit_chunks(limit)  # for testing only
            print(f"Limiting chunks to {limit}.")

        CheckpointService.init(folder=str(Path(settings.temp_folder) / self.code))
        qa_collection = get_qa_collection(self.source, self.code, self.exam.name, model)
        CheckpointService.delete_checkpoint()
        self.storage.save_to_json(data=qa_collection.to_dict(), filename="answers.json")
