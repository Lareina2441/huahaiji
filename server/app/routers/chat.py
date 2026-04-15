"""
花海纪 - 聊天路由（数据库版）
处理 AI 对话、信息抽取相关接口
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatRequest, ExtractRequest, ApiResponse
from app.database import get_db
from app import crud
from app.services.deepseek import deepseek_service
from app.services.extractor import extractor_service

router = APIRouter()


@router.post("/send", response_model=ApiResponse)
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    发送聊天消息（非流式）
    如果没有 trip_id，自动创建行程
    """
    trip_id = request.trip_id

    # 如果没有 trip_id，创建新行程
    if not trip_id:
        user_id = request.session_id or "anonymous"
        trip = await crud.create_trip(db, user_id)
        trip_id = trip.id

    # 验证行程存在
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    # 获取对话历史
    history = await crud.get_chat_history_as_list(db, trip_id)

    # 调用 DeepSeek
    try:
        result = await deepseek_service.chat_with_extract(
            user_message=request.message,
            chat_history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务异常: {str(e)}")

    # 保存对话记录到数据库
    await crud.add_chat_message(db, trip_id, "user", request.message)
    await crud.add_chat_message(db, trip_id, "assistant", result["reply"])

    return ApiResponse(
        data={
            "reply": result["reply"],
            "trip_id": trip_id,
            "is_info_complete": result["is_info_complete"],
        }
    )


@router.post("/send/stream")
async def send_message_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    发送聊天消息（流式 SSE）
    """
    trip_id = request.trip_id

    if not trip_id:
        user_id = request.session_id or "anonymous"
        trip = await crud.create_trip(db, user_id)
        trip_id = trip.id

    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    history = await crud.get_chat_history_as_list(db, trip_id)

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

        # 保存到数据库
        await crud.add_chat_message(db, trip_id, "user", request.message)
        await crud.add_chat_message(db, trip_id, "assistant", full_reply)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Trip-Id": trip_id,
        },
    )


@router.post("/extract", response_model=ApiResponse)
async def extract_info(request: ExtractRequest, db: AsyncSession = Depends(get_db)):
    """
    从对话历史中提取结构化旅行信息
    """
    trip = await crud.get_trip(db, request.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    # 获取对话历史
    messages = await crud.get_chat_history_as_list(db, request.trip_id)
    if not messages:
        raise HTTPException(status_code=404, detail="暂无对话记录")

    try:
        trip_plan = await extractor_service.extract_trip_plan(messages)
        completeness = extractor_service.check_info_completeness(trip_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"信息抽取失败: {str(e)}")

    # 保存抽取结果到行程
    await crud.update_trip(db, request.trip_id, plan=trip_plan.model_dump())

    return ApiResponse(
        data={
            "trip_plan": trip_plan.model_dump(),
            "completeness": completeness,
        }
    )


@router.get("/history/{trip_id}", response_model=ApiResponse)
async def get_chat_history(trip_id: str, db: AsyncSession = Depends(get_db)):
    """获取对话历史"""
    messages = await crud.get_chat_history(db, trip_id)
    return ApiResponse(
        data={
            "history": [{"role": m.role, "content": m.content} for m in messages],
            "trip_id": trip_id,
        }
    )


@router.delete("/history/{trip_id}", response_model=ApiResponse)
async def clear_chat_history(trip_id: str, db: AsyncSession = Depends(get_db)):
    """清空对话历史"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    await crud.clear_chat_history(db, trip_id)
    return ApiResponse(msg="对话历史已清空")
