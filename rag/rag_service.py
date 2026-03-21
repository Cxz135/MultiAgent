#rag_service.py


from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService

class RetrieverService:

    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        return self.retriever.invoke(query)

    def retrieve_formatted(self, query: str) -> str:
        docs = self.retrieve(query)

        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(
                f"[{i}] {doc.page_content}\n来源: {doc.metadata.get('source')}\n"
            )

        return "\n".join(formatted)

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
