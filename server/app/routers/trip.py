"""
花海纪 - 行程管理路由（数据库版）
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TripCreate, TripUpdate, PlaceInfo, ApiResponse
from app.database import get_db
from app import crud

router = APIRouter()


@router.post("/create", response_model=ApiResponse)
async def create_trip(request: TripCreate, db: AsyncSession = Depends(get_db)):
    """创建新行程"""
    trip = await crud.create_trip(db, request.user_id)
    return ApiResponse(data={"trip_id": trip.id})


@router.get("/list", response_model=ApiResponse)
async def list_trips(user_id: str, status: str = None, db: AsyncSession = Depends(get_db)):
    """获取用户的行程列表"""
    trips = await crud.list_user_trips(db, user_id, status)
    result = []
    for trip in trips:
        result.append({
            "id": trip.id,
            "user_id": trip.user_id,
            "plan": trip.plan_json,
            "status": trip.status,
            "summary": trip.summary,
            "created_at": trip.created_at.isoformat() if trip.created_at else "",
            "updated_at": trip.updated_at.isoformat() if trip.updated_at else "",
        })
    return ApiResponse(data=result)


@router.get("/{trip_id}", response_model=ApiResponse)
async def get_trip(trip_id: str, db: AsyncSession = Depends(get_db)):
    """获取行程详情（含地点）"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    places = await crud.get_trip_places(db, trip_id)
    places_data = [
        {
            "name": p.name, "type": p.type, "address": p.address,
            "latitude": p.latitude, "longitude": p.longitude,
            "rating": p.rating, "description": p.description,
            "price_range": p.price_range, "opening_hours": p.opening_hours,
            "tips": p.tips,
        }
        for p in places
    ]

    return ApiResponse(data={
        "id": trip.id,
        "user_id": trip.user_id,
        "plan": trip.plan_json,
        "status": trip.status,
        "summary": trip.summary,
        "places": places_data,
        "created_at": trip.created_at.isoformat() if trip.created_at else "",
        "updated_at": trip.updated_at.isoformat() if trip.updated_at else "",
    })


@router.put("/{trip_id}", response_model=ApiResponse)
async def update_trip(trip_id: str, update: TripUpdate, db: AsyncSession = Depends(get_db)):
    """更新行程"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    plan = update.plan.model_dump() if update.plan else None
    status = update.status.value if update.status else None

    trip = await crud.update_trip(db, trip_id, plan=plan, status=status)
    return ApiResponse(data={"trip_id": trip.id})


@router.delete("/{trip_id}", response_model=ApiResponse)
async def delete_trip(trip_id: str, db: AsyncSession = Depends(get_db)):
    """删除行程"""
    success = await crud.delete_trip(db, trip_id)
    if not success:
        raise HTTPException(status_code=404, detail="行程不存在")
    return ApiResponse(msg="行程已删除")


@router.get("/{trip_id}/places", response_model=ApiResponse)
async def get_trip_places(trip_id: str, db: AsyncSession = Depends(get_db)):
    """获取行程中的所有地点"""
    places = await crud.get_trip_places(db, trip_id)
    return ApiResponse(data=[
        {
            "name": p.name, "type": p.type, "address": p.address,
            "latitude": p.latitude, "longitude": p.longitude,
            "rating": p.rating, "description": p.description,
            "price_range": p.price_range, "tips": p.tips,
        }
        for p in places
    ])


@router.post("/{trip_id}/places", response_model=ApiResponse)
async def add_trip_place(trip_id: str, place: PlaceInfo, db: AsyncSession = Depends(get_db)):
    """向行程中添加地点"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    created = await crud.add_place(db, trip_id, place.model_dump())
    return ApiResponse(data={"name": created.name, "id": created.id})
