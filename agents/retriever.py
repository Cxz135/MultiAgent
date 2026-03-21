#retriever.py


from agents.base_agent import BaseAgent
from core.state import OverallState
from pydantic import BaseModel
from rag.vector_store import VectorStoreService
from rag.rag_service import RetrieverService
from utils.logger import logger


class SufficiencyJudge(BaseModel):
    sufficient: bool
    related: bool
    missing: str


class RetrieverAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        self.vector_store = VectorStoreService()
        self.retriever = RetrieverService()

    def process(self, state: OverallState) -> dict:
        query = state["messages"][-1].content
        current_course = state.get("current_course", "未分类")
        user_id = state.get("user_id", "default")
        intent = state["intent"]
        logger.info(f"在{current_course}课程中检索")

        vs_retriever = self.vector_store.get_retriever(
            course=current_course,
            user_id=user_id,
        )
        docs = vs_retriever.invoke(query)
        logger.info(f"📚 检索到 {len(docs)} 个本地文档")

        judgement = self._judge_sufficiency(query, docs, intent)

        if judgement["sufficient"]:
            return {
                "retrieved_docs": docs,
                "search_status": "local_only",
                "current_step": "retrieved",
                "missing_info":"",
            }

        if judgement["related_but_insufficient"]:
            return {
                "retrieved_docs": docs,
                "search_status": "need_web",
                "missing_info": judgement["missing"],
                "current_step": "need_web",
            }

        else:
            return {
                "intent": "irrelevant",
                "search_status": "local_only",
                "current_step": "irrelevant",
                "final_output": "抱歉，你的问题似乎和课程没有联系，换个问题吧。"

            }


    def _judge_sufficiency(self, query, docs, intent):
        form_docs = self.retriever.format_docs(docs)
        prompt = f'''
        用户想{intent}，问题是：{query}
        
        从知识库找到的文档：
        {form_docs}
        
        请判断：
        1. 这些文档能充分回答用户吗？注意：文档中有直接提到即为充分，否则不充分。(true/false)
        2. 问题和该课程相关吗(true/false)
        3. 缺少什么关键信息？
        '''
        structured_llm = self.model.with_structured_output(SufficiencyJudge)
        result = structured_llm.invoke(prompt)
        logger.info(f" 问题和课程是否相关：{result.related}  - 缺失信息: {result.missing}")
        return {
            "sufficient": result.sufficient,
            "related_but_insufficient": result.related and not result.sufficient,
            "missing": result.missing,
        }

