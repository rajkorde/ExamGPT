from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

import tiktoken
from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers import BooleanOutputParser, PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_random_exponential

from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.ai.prompts import PromptProvider
from examgpt.core.exceptions import NotEnoughInformationInContext, PromptNotFound
from examgpt.core.question import LongForm, MultipleChoice, Scenario


@dataclass
class ModelConfig:
    family: ModelFamily
    name: ModelName
    cost_ppm_token: int
    temperature: float = 0.7
    # bump the cost of by this amount to factor in input and output tokens being different price
    fuzz_factor: float = 1.3
    chunk_size: int = 2500

    def estimate_cost(self, token_count: int) -> float:
        return round(
            (token_count * self.fuzz_factor * self.cost_ppm_token) / 1_000_000, 2
        )

    def get_token_count(self, text: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.name.value)
        num_tokens = len(encoding.encode(text))
        return num_tokens


class ModelProvider(Protocol):
    def get_chat_model(self) -> BaseChatModel: ...
    def get_model_name(self) -> ModelName: ...


class AIModel_Template:
    def __init__(self, model_provider: ModelProvider):
        self.model_provider = model_provider
        self.chat = model_provider.get_chat_model()
        self.model_name = model_provider.get_model_name()
        self._prompt_provider = PromptProvider()

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def get_chat_completion(self, messages: list[SystemMessage | HumanMessage]) -> str:
        response = self.chat.invoke(messages)
        return str(response.content)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def get_chat_completion_async(
        self,
        messages: list[SystemMessage | HumanMessage],
    ) -> str:
        response = await self.chat.ainvoke(messages)
        return str(response.content)

    def _context_check(self, chunk: str, exam_name: str) -> bool:
        scenario, model = Scenario.CONTEXTCHECK, self.model_name
        prompt = self._prompt_provider.get_prompt(scenario=scenario, model=model)
        if prompt is None:
            raise PromptNotFound(
                f"Prompt not found. Scenario: {scenario}, model: {model}"
            )

        prompt = PromptTemplate(
            template=prompt,
            input_variables=["exam_name", "context"],
        )
        prompt_and_model = (
            prompt | self.chat | BooleanOutputParser(true_val="True", false_val="False")
        )
        output = prompt_and_model.invoke({"exam_name": exam_name, "context": chunk})

        return output

    def generate_longform_qa(self, chunk: str, exam_name: str) -> LongForm:
        scenario, model = Scenario.LONGFORM, self.model_name

        if not self._context_check(chunk=chunk, exam_name=exam_name):
            raise NotEnoughInformationInContext()

        prompt = self._prompt_provider.get_prompt(scenario=scenario, model=model)
        if prompt is None:
            raise PromptNotFound(
                f"Prompt not found. Scenario: {scenario}, model: {model}"
            )

        parser = PydanticOutputParser(pydantic_object=LongForm)
        prompt = PromptTemplate(
            template=prompt,
            input_variables=["exam_name", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        prompt_and_model = prompt | self.chat
        output = prompt_and_model.invoke({"exam_name": exam_name, "context": chunk})

        return parser.invoke(output)

    def generate_multiplechoice_qa(self, chunk: str, exam_name: str) -> MultipleChoice:
        scenario, model = Scenario.MULTIPLECHOICE, ModelName.DEFAULT

        if not self._context_check(chunk=chunk, exam_name=exam_name):
            raise NotEnoughInformationInContext()

        prompt = self._prompt_provider.get_prompt(scenario=scenario, model=model)
        if prompt is None:
            raise PromptNotFound(
                f"Prompt not found. Scenario: {scenario}, model: {model}"
            )

        parser = PydanticOutputParser(pydantic_object=MultipleChoice)
        prompt = PromptTemplate(
            template=prompt,
            input_variables=["exam_name", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        prompt_and_model = prompt | self.chat
        output = prompt_and_model.invoke({"exam_name": exam_name, "context": chunk})

        return parser.invoke(output)

    def generate_answer(self, chunk: str, question: str, exam_name: str) -> str:
        raise NotImplementedError()


class AIModel:
    # defining __init__ in ABC to force sub class to define these instance variables
    def __init__(self, model_provider: ModelProvider, chat: BaseChatModel):
        self.model_config = model_provider
        self.chat = chat

    @abstractmethod
    def generate_longform_qa(self, chunk: str, exam_name: str) -> LongForm: ...

    @abstractmethod
    def generate_multiplechoice_qa(
        self, chunk: str, exam_name: str
    ) -> MultipleChoice: ...

    @abstractmethod
    def generate_answer(self, chunk: str, question: str, exam_name: str) -> str: ...
