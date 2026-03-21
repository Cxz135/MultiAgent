#base_agent.py


from abc import ABC, abstractmethod
from core.state import OverallState
from utils.config_handler import prompts_config


class BaseAgent(ABC):

    def __init__(self, model):
        self.model = model
        self.config = prompts_config

    @abstractmethod
    def process(self, state: OverallState) -> dict:
        pass

    def get_prompt(self, **kwargs) -> str:
        prompt_template = self.config[self.__class__.__name__]
        return prompt_template.format(**kwargs)

    def format_docs(self, docs) -> str:

        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(
                f"[{i}] {doc.page_content}\n来源: {doc.metadata.get('source')}\n"
            )

        return "\n".join(formatted)