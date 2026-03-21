#app/api/chat.py


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.cache import cache
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from core.graph import create_agent_graph
import json


router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    user_id: str = 'default'
    note_style: str = 'detailed'
    current_course: str = 'default'

class ChatResponse(BaseModel):
    answer: str
    intent: str
    sources: list


@router.post("", response_model=ChatResponse)  # 改回普通POST
async def chat(request: ChatRequest):

    cache_key = cache.generate_key(request.query, request.note_style)
    cache_result = cache.get(cache_key)
    if cache_result:
        print(f"✅ 命中缓存: {request.query[:30]}...")
        return cache_result

    """普通POST接口"""
    graph = create_agent_graph()

    state = {
        "messages": [HumanMessage(content=request.query)],
        "current_course": request.current_course or "未分类",
        "retrieved_docs": [],
        "intent": None,
        "current_step": "start",
        "search_status": None,
        "final_output": None,
        "user_id": 'default',
        "note_style": request.note_style,
        "missing_info": None,
    }

    result = await graph.ainvoke(state)

    response_data = {
        "answer": result.get("final_output", ""),
        "intent": result.get("intent", ""),
        "sources": [doc.metadata.get("source", "") for doc in result.get("retrieved_docs", [])]
    }
    cache.set(cache_key, response_data)
    return ChatResponse(**response_data)

