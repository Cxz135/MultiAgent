#note.py


from agents.base_agent import BaseAgent
from core.state import OverallState
from typing import Dict, Any


class NoteAgent(BaseAgent):

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        docs = state["retrieved_docs"]
        query = state["messages"][-1].content
        formatted = self.format_docs(docs)

        prompt = self.get_prompt(
            query=query,
            source_materials=formatted,
        )
        response = await self.model.ainvoke(prompt)
        return {"final_output": response.content}