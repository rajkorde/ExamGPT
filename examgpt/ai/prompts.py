import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from examgpt.ai.constants import ModelName
from examgpt.core.question import Scenario


@dataclass
@dataclass_json
class Prompt:
    scenario: Scenario
    model: ModelName
    prompt: str


class PromptProvider:
    prompts_file: str = "prompts.json"

    def __init__(self):
        with open(self.prompts_file, "r") as f:
            prompts = json.load(f)
            self.prompts = [Prompt.from_dict(prompt) for prompt in prompts]  # type: ignore

    def get_prompt(self, scenario: Scenario, model: ModelName) -> str | None:
        for prompt in self.prompts:
            if prompt.scenario == scenario and prompt.model == model:
                return prompt.prompt  # return first hit

        return None
