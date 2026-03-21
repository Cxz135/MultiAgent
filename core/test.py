#test.py


import sys
import os
from rag.vector_store import VectorStoreService

import asyncio
from core.graph import create_agent_graph


async def test_graph():
    """测试Agent图"""

    # 创建图
    print("🟢 进入 test_graph 函数")

    print("🟡 正在创建 Agent 图...")
    graph = create_agent_graph()
    print("✅ Agent 图创建完成")

    # 测试用例1：出题
    test_cases = [
        {
            "name": "出题测试",
            "input": "Please give me some machine learning questions.",
            "expected_intent": "question_generate"
        },
        {
            "name": "笔记测试",
            "input": "帮我整理一下Machine Learning的笔记",
            "expected_intent": "note"
        },
        {
            "name": "问答测试",
            "input": "什么是深度学习？",
            "expected_intent": "qa"
        },
        {
            "name": "不相关测试",
            "input": "今天天气怎么样？",
            "expected_intent": "irrelevant"
        }
    ]

    for case in test_cases:
        print(f"\n{'=' * 50}")
        print(f"测试: {case['name']}")
        print(f"输入: {case['input']}")
        print('=' * 50)

        # 初始状态
        state = {
            "messages": [{"role": "user", "content": case["input"]}],
            "intent": None,
            "retrieved_docs": [],
            "current_step": "start"
        }

        # 运行图
        result = await graph.ainvoke(state)

        # 输出结果
        print(f"\n意图识别: {result.get('intent')}")
        print(f"期望意图: {case['expected_intent']}")
        print(f"检索文档数: {len(result.get('retrieved_docs', []))}")
        print(f"最终输出: {result.get('final_output', '')[:200]}...")
        print(f"当前步骤: {result.get('current_step')}")


if __name__ == '__main__':
    vs = VectorStoreService()
    vs.load_document()
    asyncio.run(test_graph())