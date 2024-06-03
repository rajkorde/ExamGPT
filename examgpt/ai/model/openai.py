from dataclasses import dataclass, field

from langchain.output_parsers import BooleanOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from examgpt.ai.base import AIModel, ModelConfig
from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.ai.prompts import PromptProvider
from examgpt.core.exceptions import NotEnoughInformationInContext, PromptNotFound
from examgpt.core.question import LongForm, MultipleChoice, Scenario


@dataclass
class OpenAIConfig(ModelConfig):
    family: ModelFamily = field(default=ModelFamily.OPENAI)
    name: ModelName = field(default=ModelName.GPT3_5_TURBO)
    cost_ppm_token: int = 50
    chunk_size: int = 2500


class OpenAIModel(AIModel):
    def __init__(self):
        self.model_config = OpenAIConfig()
        self.chat = ChatOpenAI(model=str(self.model_config.name.value))
        self._prompt_provider = PromptProvider()

    def _context_check(self, chunk: str, exam_name: str) -> bool:
        scenario, model = Scenario.CONTEXTCHECK, ModelName.DEFAULT
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
        scenario, model = Scenario.LONGFORM, ModelName.DEFAULT

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
