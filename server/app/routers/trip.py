"""
花海纪 - 行程管理路由
处理行程的创建、查询、更新、删除
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.models import (
    TripCreate, TripUpdate, TripPlan, TripStatus,
    PlaceInfo, ApiResponse,
)

router = APIRouter()

# 内存存储（生产环境替换为数据库）
_trip_db: dict[str, dict] = {}


@router.post("/create", response_model=ApiResponse)
async def create_trip(request: TripCreate):
    """创建新行程"""
    trip_id = str(uuid.uuid4())
    trip = {
        "id": trip_id,
        "user_id": request.user_id,
        "plan": {},
        "status": "draft",
        "places": [],
        "summary": "",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _trip_db[trip_id] = trip
    return ApiResponse(data={"trip_id": trip_id})


@router.get("/list", response_model=ApiResponse)
async def list_trips(user_id: str, status: str | None = None):
    """获取用户的行程列表"""
    trips = [
        trip for trip in _trip_db.values()
        if trip["user_id"] == user_id
        and (status is None or trip["status"] == status)
    ]
    # 按创建时间倒序
    trips.sort(key=lambda x: x["created_at"], reverse=True)
    return ApiResponse(data=trips)


@router.get("/{trip_id}", response_model=ApiResponse)
async def get_trip(trip_id: str):
    """获取行程详情"""
    trip = _trip_db.get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return ApiResponse(data=trip)


@router.put("/{trip_id}", response_model=ApiResponse)
async def update_trip(trip_id: str, update: TripUpdate):
    """更新行程"""
    trip = _trip_db.get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    if update.plan:
        trip["plan"] = update.plan.model_dump()
    if update.status:
        trip["status"] = update.status.value
    if update.places:
        trip["places"] = [p.model_dump() for p in update.places]
    trip["updated_at"] = datetime.utcnow().isoformat()

    return ApiResponse(data=trip)


@router.delete("/{trip_id}", response_model=ApiResponse)
async def delete_trip(trip_id: str):
    """删除行程"""
    if trip_id in _trip_db:
        del _trip_db[trip_id]
        return ApiResponse(msg="行程已删除")
    raise HTTPException(status_code=404, detail="行程不存在")


@router.get("/{trip_id}/places", response_model=ApiResponse)
async def get_trip_places(trip_id: str):
    """获取行程中的所有地点"""
    trip = _trip_db.get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return ApiResponse(data=trip.get("places", []))


@router.post("/{trip_id}/places", response_model=ApiResponse)
async def add_trip_place(trip_id: str, place: PlaceInfo):
    """向行程中添加地点"""
    trip = _trip_db.get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    places = trip.get("places", [])
    places.append(place.model_dump())
    trip["places"] = places
    trip["updated_at"] = datetime.utcnow().isoformat()

    return ApiResponse(data=place.model_dump())
