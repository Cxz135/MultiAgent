# agents/answer.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, AsyncGenerator
from utils.logger import logger
import time


class AnswerAgent(BaseAgent):

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """非流式版本（用于缓存等场景）"""
        logger.info(f"🤖 开始生成回答...")
        docs = state["retrieved_docs"]
        query = state["messages"][-1].content
        formatted = self.format_docs(docs)

        prompt = self.get_prompt(
            query=query,
            reference_materials=formatted,
        )

        response = await self.model.ainvoke(prompt)
        logger.info(f"✅ 回答生成完成")
        return {"final_output": response.content}

    async def stream_process(self, state: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """流式处理版本"""
        logger.info(f"🤖 开始流式生成回答...")
        docs = state["retrieved_docs"]
        query = state["messages"][-1].content
        formatted = self.format_docs(docs)

        prompt = self.get_prompt(
            query=query,
            reference_materials=formatted,
        )

        # 流式输出
        async for chunk in self.model.astream(prompt):
            yield chunk.content