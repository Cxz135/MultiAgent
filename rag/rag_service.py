#rag_service.py


from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService

class RetrieverService:

    def __init__(self):
        self.vector_store = VectorStoreService()

    def get_retriever(self, course: str, user_id: str = "default"):
        """根据课程获取检索器（延迟创建）"""
        return self.vector_store.get_retriever(course=course, user_id=user_id)

    def retrieve(self, query: str, course: str, user_id: str = "default", k: int = 5) -> list[Document]:
        """检索文档，需要传入课程"""
        retriever = self.get_retriever(course, user_id)
        return retriever.invoke(query)

    def retrieve_formatted(self, query: str, course: str, user_id: str = "default") -> str:
        """检索并格式化，需要传入课程"""
        docs = self.retrieve(query, course, user_id)
        return self.format_docs(docs)

    def format_docs(self, docs) -> str:
        """直接格式化已有的docs"""
        if not docs:
            return "没有找到相关文档"

        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(
                f"[{i}] {doc.page_content}\n来源: {doc.metadata.get('source', '未知')}\n"
            )
        return "\n".join(formatted)
