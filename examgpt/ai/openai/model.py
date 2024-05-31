from dataclasses import dataclass, field

from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from examgpt.ai.base import AIModel, ModelConfig
from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.ai.prompts import PromptProvider
from examgpt.core.exceptions import PromptNotFound
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
        context_checker_prompt = f"""
Your overall goal is to help me prepare for the {exam_name}. 

Assume that there is a robot that can generate a question and answer pair to help 
me practice for the exam. But this robot doesnt generate good questions and answers if
provided text is of low quality.

I will give you some text, and your job is to respond with yes or no 
depending on whether the text contains enough meaningful information for the robot to 
create a good quality question and answer relevant for the exam. 

Examples of bad text includes:
- not enough text to formulate to good quality question and answer
- text that contains too many short phrases instead of full english sentences
- text that is irrelevant to the exam
- text that looks like table of contents
- text that looks like information about how to take the exam

Examples of good text include: 
- text that is directly related to questions that will be asked in the the exam
"""
        messages = [
            SystemMessage(content=context_checker_prompt),
            HumanMessage(content=text),
        ]
        return get_chat_completion(messages)

    #     def generate_longform_qa(self, chunk: str, exam_name: str) -> LongForm:
    #         long_form_qa_generator_prompt = f"""
    # Your job is a prepare a quiz that will help me prepare for the {exam_name}.
    # I will give you some text and your job is to generate a question and answer based on that tex.
    # The question and answer should be short and concise.
    # The question and answer should be relevant to the exam
    # In your question generation, make no mention of the fact that you are given some text.
    # For example, dont create questions like "what are the 4 drawbacks mentioned in the text?"
    # The questions should contain enough context to come up with the answer.
    # """

    def generate_longform_qa(self, chunk: str, exam_name: str) -> LongForm:
        scenario, model = Scenario.LONGFORM, ModelName.DEFAULT
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

    def generate_multiplechoice_qa(self, chunk: str) -> MultipleChoice: ...

    def generate_answer(self, chunk: str, question: str) -> str: ...
