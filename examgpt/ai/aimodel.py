from langchain.output_parsers import BooleanOutputParser, PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from examgpt.ai.base import ModelConfig, ModelProvider
from examgpt.ai.prompts import PromptProvider
from examgpt.core.exceptions import NotEnoughInformationInContext, PromptNotFound
from examgpt.core.question import LongForm, MultipleChoice, Scenario
from examgpt.sources.chunkers.base import TextChunk


class AIModel:
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

    def get_model_config(self) -> ModelConfig:
        return self.model_provider.get_model_config()

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

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_not_exception_type(NotEnoughInformationInContext),
        reraise=True,
    )
    def generate_longform_qa(self, chunk: TextChunk, exam_name: str) -> LongForm:
        scenario, model = Scenario.LONGFORM, self.model_name

        if not self._context_check(chunk=chunk.text, exam_name=exam_name):
            raise NotEnoughInformationInContext(chunk.id)

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

        output = prompt_and_model.invoke(
            {"exam_name": exam_name, "context": chunk.text}
        )

        return parser.invoke(output)

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_not_exception_type(NotEnoughInformationInContext),
        reraise=True,
    )
    def generate_multiplechoice_qa(
        self, chunk: TextChunk, exam_name: str
    ) -> MultipleChoice:
        scenario, model = Scenario.MULTIPLECHOICE, self.model_name

        if not self._context_check(chunk=chunk.text, exam_name=exam_name):
            raise NotEnoughInformationInContext(chunk.id)

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
        output = prompt_and_model.invoke(
            {"exam_name": exam_name, "context": chunk.text}
        )

        return parser.invoke(output)

    def generate_answer(self, chunk: str, question: str, exam_name: str) -> str:
        raise NotImplementedError()
