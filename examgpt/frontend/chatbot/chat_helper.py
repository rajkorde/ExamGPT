import json
import random
from pathlib import Path
from typing import Optional

from loguru import logger

from examgpt.core.config import ApplicationSettings
from examgpt.core.question import MultipleChoiceEnhanced, QACollection
from examgpt.storage.base import StorageType
from examgpt.storage.files import FileStorage

settings = ApplicationSettings()  # pyright: ignore


class ChatHelper:
    def __init__(self):
        self.storage = None
        self.qacollection = None

    def initialize(self, exam_id: str, storage_type: StorageType = StorageType.FILE):
        if storage_type == StorageType.FILE:
            exam_folder = Path(settings.temp_folder) / exam_id

            if not exam_folder.exists():
                return None

            storage = FileStorage(folder=str(exam_folder))
            self.qacollection = storage.get_qa_collection(location="answers.json")

            with Path(exam_folder / "answers.json").open("r") as f:
                data = json.load(f)

            self.qacollection = QACollection.from_dict(data)

            if not self.qacollection.long_form_qa:
                logger.warning("No long form questions found")
            if not self.qacollection.multiple_choice_qa:
                logger.warning("No multiple choice questions found")

        elif storage_type == StorageType.CLOUD:
            raise NotImplementedError()

        return self.qacollection.exam_id

    def get_helper(self, exam_id: str): ...

    def multiple_choice(self, topic: str = "") -> Optional[MultipleChoiceEnhanced]:
        if self.qacollection.multiple_choice_qa is not None:
            question = random.choice(self.qacollection.multiple_choice_qa)
        else:
            question = None
        return question

    def longform(self, n: int = 1, topic: str = ""):
        if self.qacollection.long_form_qa is not None:
            question = random.choice(self.qacollection.long_form_qa)
        else:
            question = None
        return question

    def answer(self, question: str): ...
