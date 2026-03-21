#router.py

from agents.base_agent import BaseAgent
from core.state import OverallState
from utils.logger import logger

class RouterAgent(BaseAgent):

    def process(self, state: OverallState) -> dict:
        query = state["messages"][-1].content
        prompt = self.get_prompt(user_input = query)
        response = self.model.invoke(prompt)
        intent = self._parse_intent(response.content)
        logger.info(f"检测到用户的意图是{intent}")
        return {
            "intent": intent,
            "current_step": "router_done"
        }

    def _parse_intent(self, response: str) -> str:
        if "问答" in response:
            return "qa"
        elif "笔记" in response:
            return "note"
        elif "出题" in response:
            return "question_generate"
        else:
            return "irrelevant"



