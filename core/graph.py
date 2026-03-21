#graph.py


from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from core.state import OverallState

from agents.retriever import RetrieverAgent
from agents.router import RouterAgent
from agents.note import NoteAgent
from agents.question_generate import QuestionGeneratorAgent
from agents.answer import AnswerAgent
from agents.web_search import WebSearchAgent
from model.factory import get_chat_model
from utils.logger import logger

def create_agent_graph():

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

    def route_by_intent(state: OverallState) -> dict:
        """根据 intent 决定去哪个生成节点"""
        return {"intent": state.get("intent", "qa")}

    graph.add_node("intent_router", route_by_intent)

    graph.set_entry_point("router")
    graph.add_edge("router", "retriever")

    graph.add_conditional_edges(
        "retriever",
        lambda state: state.get("current_step"),
        {
            "retrieved": "intent_router",           # 本地足够 → 直接回答
            "need_web": "web_search",         # 需要联网 → 去搜索
            "irrelevant": END                  # 不相关 → 结束
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
    #graph.add_conditional_edges()
    graph.add_edge("question_generator", END)
    graph.add_edge("answer", END)
    graph.add_edge("note", END)
    graph.add_edge("irrelevant_handler", END)

    return graph.compile()


def irrelevant_handler_node(state: OverallState):
    return {
        "final_output": state.get(
            "final_output",
            "抱歉，知识库中没有找到相关信息。"
        )
    }


