# core/graph.py - 只保留流式函数，去掉麻烦的部分
from langgraph.graph import StateGraph, START, END
from core.state import OverallState
from agents.retriever import RetrieverAgent
from agents.router import RouterAgent
from agents.note import NoteAgent
from agents.question_generate import QuestionGeneratorAgent
from agents.answer import AnswerAgent
from agents.web_search import WebSearchAgent
from model.factory import get_chat_model
from utils.logger import logger
from typing import AsyncGenerator, Dict, Any


def create_agent_graph():
    """创建非流式图（用于普通调用）"""
    model = get_chat_model()
    router = RouterAgent(model)
    retriever = RetrieverAgent(model)
    question_gen = QuestionGeneratorAgent(model)
    answer = AnswerAgent(model)
    note = NoteAgent(model)
    web_search = WebSearchAgent(model)

    graph = StateGraph(OverallState)
    graph.add_node("router", router.process)
    graph.add_node("retriever", retriever.process)
    graph.add_node("question_generator", question_gen.process)
    graph.add_node("answer", answer.process)
    graph.add_node("note", note.process)
    graph.add_node("web_search", web_search.process)
    graph.add_node("irrelevant_handler", irrelevant_handler_node)
    graph.add_node("intent_router", route_by_intent)

    graph.set_entry_point("router")
    graph.add_edge("router", "retriever")

    graph.add_conditional_edges(
        "retriever",
        lambda state: state.get("current_step"),
        {
            "retrieved": "intent_router",
            "need_web": "web_search",
            "irrelevant": END
        }
    )
    graph.add_edge("web_search", "intent_router")

    graph.add_conditional_edges(
        "intent_router",
        lambda state: state.get("intent", ""),
        {
            "qa": "answer",
            "question_generate": "question_generator",
            "note": "note",
            "irrelevant": "irrelevant_handler",
        }
    )
    graph.add_edge("question_generator", END)
    graph.add_edge("answer", END)
    graph.add_edge("note", END)
    graph.add_edge("irrelevant_handler", END)

    return graph.compile()


async def stream_agent(state: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """
    流式执行Agent（简化版，只处理问答意图）
    """
    model = get_chat_model()
    router = RouterAgent(model)
    retriever = RetrieverAgent(model)
    answer = AnswerAgent(model)
    web_search = WebSearchAgent(model)

    try:
        # 1. 路由
        router_result = await router.process(state)
        state.update(router_result)

        intent = state.get("intent", "")

        if intent != "qa":
            # 非问答意图暂不支持流式
            logger.warning(f"意图 {intent} 暂不支持流式")
            # 改用完整graph处理
            graph = create_agent_graph()
            result = await graph.ainvoke(state)
            yield result.get("final_output", "")
            return

        # 2. 检索
        retriever_result = await retriever.process(state)
        state.update(retriever_result)

        # 3. 如果需要联网
        if state.get("current_step") == "need_web":
            web_result = await web_search.process(state)
            state.update(web_result)

        # 4. 流式生成回答
        async for chunk in answer.stream_process(state):
            yield chunk

    except Exception as e:
        logger.error(f"流式生成失败: {e}", exc_info=True)
        yield f"抱歉，生成回答时发生错误: {str(e)}"


def route_by_intent(state: OverallState) -> dict:
    return {"intent": state.get("intent", "qa")}


def irrelevant_handler_node(state: OverallState):
    return {
        "final_output": state.get(
            "final_output",
            "抱歉，知识库中没有找到相关信息。"
        )
    }