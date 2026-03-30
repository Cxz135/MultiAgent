# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.cache import cache
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from core.graph import create_agent_graph
from utils.logger import logger
import json
import asyncio

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


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """普通POST接口（带缓存）"""

    # 1. 先查语义缓存
    logger.info(f"🔍 查询缓存: {request.query[:50]}...")
    cached_result = cache.get(
        query=request.query,
        course=request.current_course,
        intent="qa"
    )

    if cached_result:
        logger.info(f"✅ 语义缓存命中: {request.query[:30]}...")
        return ChatResponse(
            answer=cached_result.get("answer", ""),
            intent=cached_result.get("intent", ""),
            sources=cached_result.get("sources", [])
        )

    logger.info(f"📝 缓存未命中，执行正常流程...")

    # 2. 未命中，执行正常流程
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

    # 3. 存入缓存
    logger.info(f"💾 准备存储到缓存: {request.query[:50]}...")
    success = cache.set(
        query=request.query,
        value=response_data,  # ✅ 关键：参数名是 value
        course=request.current_course,
        intent=result.get("intent", "qa")
    )

    if success:
        logger.info(f"✅ 语义缓存存储成功: {request.query[:50]}...")
    else:
        logger.warning(f"❌ 语义缓存存储失败: {request.query[:50]}...")

    return ChatResponse(**response_data)


# 流式接口（也支持缓存）
@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式接口（带缓存）
    """
    from core.graph import stream_agent

    # 1. 先检查缓存
    logger.info(f"🔍 [流式] 查询缓存: {request.query[:50]}...")
    cached_result = cache.get(
        query=request.query,
        course=request.current_course,
        intent="qa"
    )

    # 2. 缓存命中，模拟流式返回
    if cached_result:
        logger.info(f"✅ [流式] 语义缓存命中: {request.query[:30]}...")

        async def stream_cached():
            answer = cached_result.get("answer", "")
            # 模拟流式输出（逐字返回）
            for i in range(0, len(answer), 3):
                yield f"data: {json.dumps({'content': answer[i:i + 3], 'done': False})}\n\n"
                await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        return StreamingResponse(
            stream_cached(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    # 3. 未命中，执行正常流程
    logger.info(f"📝 [流式] 缓存未命中，执行正常流程...")

    async def generate():
        state = {
            "messages": [HumanMessage(content=request.query)],
            "current_course": request.current_course or "未分类",
            "retrieved_docs": [],
            "intent": None,
            "current_step": "start",
            "search_status": None,
            "final_output": None,
            "user_id": request.user_id,
            "note_style": request.note_style,
            "missing_info": None,
        }

        full_response = []

        try:
            async for chunk in stream_agent(state):
                full_response.append(chunk)
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # 流式结束后存入缓存
            complete_answer = "".join(full_response)
            if complete_answer:
                response_data = {
                    "answer": complete_answer,
                    "intent": state.get("intent", "qa"),
                    "sources": [doc.metadata.get("source", "") for doc in state.get("retrieved_docs", [])]
                }

                logger.info(f"💾 [流式] 准备存储到缓存: {request.query[:50]}...")
                success = cache.set(
                    query=request.query,
                    value=response_data,
                    course=request.current_course,
                    intent=state.get("intent", "qa")
                )

                if success:
                    logger.info(f"✅ [流式] 语义缓存存储成功: {request.query[:50]}...")
                else:
                    logger.warning(f"❌ [流式] 语义缓存存储失败: {request.query[:50]}...")

            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        except Exception as e:
            logger.error(f"流式生成失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )