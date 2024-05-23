from abc import ABC
from dataclasses import dataclass


@dataclass
class QuestionAnswer(ABC):
    question: str
    answer: str


@dataclass
class LongForm(QuestionAnswer):
    def __repr__(self) -> str:
        return f"Question: {self.question}\nAnswer: {self.answer}"


@dataclass
class MultipleChoice(QuestionAnswer):
    choices: list[str]

    def __repr__(self) -> str:
        return (
            f"Question: {self.question}\n"
            + f"Choices: \n{"\n".join(self.choices)}\n"
            + f"Answer: {self.answer}"
        )
