"""
花海纪 - 聊天路由
处理 AI 对话、信息抽取相关接口
"""
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

from app.models import (
    ChatRequest, ChatResponse, ExtractRequest,
    TripPlan, ApiResponse,
)
from app.services.deepseek import deepseek_service
from app.services.extractor import extractor_service

router = APIRouter()

# 内存存储：trip_id -> 对话历史（生产环境应使用数据库）
_chat_store: dict[str, list[dict]] = {}


@router.post("/send", response_model=ApiResponse)
async def send_message(request: ChatRequest):
    """
    发送聊天消息（非流式）
    """
    trip_id = request.trip_id or str(uuid.uuid4())

    # 获取对话历史
    history = _chat_store.get(trip_id, [])

    # 调用 DeepSeek
    try:
        result = await deepseek_service.chat_with_extract(
            user_message=request.message,
            chat_history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务异常: {str(e)}")

    # 更新对话历史
    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": result["reply"]})
    _chat_store[trip_id] = history

    return ApiResponse(
        data={
            "reply": result["reply"],
            "trip_id": trip_id,
            "is_info_complete": result["is_info_complete"],
        }
    )


@router.post("/send/stream")
async def send_message_stream(request: ChatRequest):
    """
    发送聊天消息（流式 SSE）
    """
    trip_id = request.trip_id or str(uuid.uuid4())
    history = _chat_store.get(trip_id, [])

    async def event_generator():
        full_reply = ""
        try:
            async for chunk in deepseek_service.chat_stream(
                user_message=request.message,
                chat_history=history,
            ):
                full_reply += chunk
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

        yield f"data: [DONE]\n\n"

        # 流结束后更新历史
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": full_reply})
        _chat_store[trip_id] = history

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Trip-Id": trip_id,
        },
    )


@router.post("/extract", response_model=ApiResponse)
async def extract_info(request: ExtractRequest):
    """
    从对话历史中提取结构化旅行信息
    """
    history = _chat_store.get(request.trip_id)
    if not history:
        raise HTTPException(status_code=404, detail="未找到对应的对话记录")

    try:
        trip_plan = await extractor_service.extract_trip_plan(history)
        completeness = extractor_service.check_info_completeness(trip_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"信息抽取失败: {str(e)}")

    return ApiResponse(
        data={
            "trip_plan": trip_plan.model_dump(),
            "completeness": completeness,
        }
    )


@router.get("/history/{trip_id}", response_model=ApiResponse)
async def get_chat_history(trip_id: str):
    """获取对话历史"""
    history = _chat_store.get(trip_id, [])
    return ApiResponse(data={"history": history, "trip_id": trip_id})


@router.delete("/history/{trip_id}", response_model=ApiResponse)
async def clear_chat_history(trip_id: str):
    """清空对话历史"""
    if trip_id in _chat_store:
        del _chat_store[trip_id]
    return ApiResponse(msg="对话历史已清空")
