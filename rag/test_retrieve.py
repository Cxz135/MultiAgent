# test_retrieve.py
from rag.vector_store import VectorStoreService
import asyncio


async def test_retrieve():
    vs = VectorStoreService()

    # 测试不同查询
    test_queries = [
        "knn",
        "KNN",
        "K-最近邻",
        "K近邻算法",
        "机器学习"
    ]

    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        print("-" * 40)

        # 获取检索器（不加过滤）
        retriever = vs.get_retriever()
        docs = await retriever.ainvoke(query)

        print(f"找到 {len(docs)} 个文档")
        for i, doc in enumerate(docs[:3]):  # 只显示前3个
            print(f"\n文档 {i + 1}:")
            print(f"内容预览: {doc.page_content[:200]}...")
            print(f"课程: {doc.metadata.get('course', '未知')}")
            print(f"来源: {doc.metadata.get('source', '未知')}")


if __name__ == "__main__":
    asyncio.run(test_retrieve())