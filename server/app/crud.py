"""
花海纪 - 数据库 CRUD 操作封装
提供用户、行程、地点、聊天记录的增删改查
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import UserModel, TripModel, PlaceModel, ChatMessageModel


# ==================== 用户 ====================

async def create_user(db: AsyncSession, openid: str, nickname: str = "", avatar: str = "") -> UserModel:
    """创建用户"""
    user = UserModel(
        id=str(uuid.uuid4()),
        openid=openid,
        nickname=nickname,
        avatar=avatar,
    )
    db.add(user)
    await db.flush()
    return user


async def get_user_by_openid(db: AsyncSession, openid: str) -> Optional[UserModel]:
    """通过 openid 获取用户"""
    result = await db.execute(select(UserModel).where(UserModel.openid == openid))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[UserModel]:
    """通过 ID 获取用户"""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


# ==================== 行程 ====================

async def create_trip(db: AsyncSession, user_id: str) -> TripModel:
    """创建行程"""
    trip = TripModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        status="draft",
    )
    db.add(trip)
    await db.flush()
    return trip


async def get_trip(db: AsyncSession, trip_id: str) -> Optional[TripModel]:
    """获取行程"""
    result = await db.execute(select(TripModel).where(TripModel.id == trip_id))
    return result.scalar_one_or_none()


async def list_user_trips(
    db: AsyncSession,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[TripModel]:
    """获取用户的行程列表"""
    query = select(TripModel).where(TripModel.user_id == user_id)
    if status:
        query = query.where(TripModel.status == status)
    query = query.order_by(desc(TripModel.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_trip(
    db: AsyncSession,
    trip_id: str,
    plan: Optional[dict] = None,
    status: Optional[str] = None,
    summary: Optional[str] = None,
) -> Optional[TripModel]:
    """更新行程"""
    trip = await get_trip(db, trip_id)
    if not trip:
        return None
    if plan is not None:
        trip.plan_json = plan
    if status is not None:
        trip.status = status
    if summary is not None:
        trip.summary = summary
    trip.updated_at = datetime.utcnow()
    await db.flush()
    return trip


async def delete_trip(db: AsyncSession, trip_id: str) -> bool:
    """删除行程"""
    trip = await get_trip(db, trip_id)
    if not trip:
        return False
    # 同时删除关联的地点和聊天记录
    await db.execute(delete(PlaceModel).where(PlaceModel.trip_id == trip_id))
    await db.execute(delete(ChatMessageModel).where(ChatMessageModel.trip_id == trip_id))
    await db.delete(trip)
    await db.flush()
    return True


# ==================== 地点 ====================

async def add_place(db: AsyncSession, trip_id: str, place_data: dict) -> PlaceModel:
    """添加地点到行程"""
    place = PlaceModel(
        id=str(uuid.uuid4()),
        trip_id=trip_id,
        **place_data,
    )
    db.add(place)
    await db.flush()
    return place


async def get_trip_places(db: AsyncSession, trip_id: str) -> list[PlaceModel]:
    """获取行程中的所有地点"""
    result = await db.execute(
        select(PlaceModel)
        .where(PlaceModel.trip_id == trip_id)
        .order_by(PlaceModel.sort_order, PlaceModel.created_at)
    )
    return list(result.scalars().all())


async def clear_trip_places(db: AsyncSession, trip_id: str):
    """清空行程中的所有地点"""
    await db.execute(delete(PlaceModel).where(PlaceModel.trip_id == trip_id))
    await db.flush()


async def batch_add_places(db: AsyncSession, trip_id: str, places: list[dict]) -> list[PlaceModel]:
    """批量添加地点"""
    await clear_trip_places(db, trip_id)
    created = []
    for i, place_data in enumerate(places):
        place_data.setdefault("sort_order", i)
        place = await add_place(db, trip_id, place_data)
        created.append(place)
    return created


# ==================== 聊天记录 ====================

async def add_chat_message(
    db: AsyncSession,
    trip_id: str,
    role: str,
    content: str,
) -> ChatMessageModel:
    """添加聊天记录"""
    msg = ChatMessageModel(
        id=str(uuid.uuid4()),
        trip_id=trip_id,
        role=role,
        content=content,
    )
    db.add(msg)
    await db.flush()
    return msg


async def get_chat_history(
    db: AsyncSession,
    trip_id: str,
    limit: int = 50,
) -> list[ChatMessageModel]:
    """获取对话历史（按时间正序）"""
    result = await db.execute(
        select(ChatMessageModel)
        .where(ChatMessageModel.trip_id == trip_id)
        .order_by(ChatMessageModel.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_chat_history_as_list(
    db: AsyncSession,
    trip_id: str,
    limit: int = 50,
) -> list[dict]:
    """获取对话历史（返回 dict 列表，用于发送给 AI）"""
    messages = await get_chat_history(db, trip_id, limit)
    return [{"role": m.role, "content": m.content} for m in messages]


async def clear_chat_history(db: AsyncSession, trip_id: str):
    """清空对话历史"""
    await db.execute(delete(ChatMessageModel).where(ChatMessageModel.trip_id == trip_id))
    await db.flush()
