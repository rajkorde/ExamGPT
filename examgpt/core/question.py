from enum import Enum

from langchain_core.pydantic_v1 import BaseModel, Field


class Scenario(Enum):
    LONGFORM = "long_form"
    MULTIPLECHOICE = "multiple_choice"
    ANSWER = "answer"


class LongForm(BaseModel):
    question: str = Field(description="An exam question with a longform answer")
    answer: str = Field(description="A longform answer to an exam question")

    # TODO: add validators

    def __repr__(self) -> str:
        return f"Question: {self.question}\nAnswer: {self.answer}"


class MultipleChoice(BaseModel):
    question: str = Field(description="An exam question with a multiple choice answers")
    answer: str = Field(description="Answer to a multiple choice question")
    choices: list[str] = Field(
        description="A list of 4 choices for an exam question, out of which one is corrrect",
        max_items=4,
    )

    # TODO: add validators

    def __repr__(self) -> str:
        return (
            f"Question: {self.question}\n"
            + f"Choices: \n{"\n".join(self.choices)}\n"
            + f"Answer: {self.answer}"
        )
