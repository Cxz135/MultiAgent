#router.py

from agents.base_agent import BaseAgent
from core.state import OverallState
from utils.logger import logger
from model.factory import get_light_model
import time

class RouterAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        # Router也用轻量模型做意图识别
        self.router_model = get_light_model()
        logger.info("RouterAgent初始化，使用轻量模型做意图识别")

    async def process(self, state: OverallState) -> dict:
        start_time = time.time()
        query = state["messages"][-1].content
        prompt = self.get_prompt(user_input = query)
        response = await self.router_model.ainvoke(prompt)
        intent = self._parse_intent(response.content)
        elapsed = time.time() - start_time
        logger.info(f"检测到用户的意图是{intent}, 耗时{elapsed:.2f}秒")
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



