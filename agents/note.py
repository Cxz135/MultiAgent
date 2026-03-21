#note.py


from agents.base_agent import BaseAgent
from core.state import OverallState
from typing import Dict, Any


class NoteAgent(BaseAgent):

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        docs = state["retrieved_docs"]
        query = state["messages"][-1].content
        formatted = self.format_docs(docs)

        prompt = self.get_prompt(
            query=query,
            source_materials=formatted,
        )
        response = self.model.invoke(prompt)
        return {"final_output": response.content}