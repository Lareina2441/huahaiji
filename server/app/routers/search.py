"""
花海纪 - 搜索路由（数据库版）
处理旅行计划确认、搜索推荐相关接口
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    SearchRequest, TripPlan, ApiResponse, SearchResult, PlaceInfo,
)
from app.database import get_db
from app import crud
from app.services.searcher import searcher_service
from app.services.mapper import mapper_service

router = APIRouter()


class ConfirmPlanRequest(TripPlan):
    """确认旅行计划请求"""
    trip_id: str


@router.post("/confirm-plan", response_model=ApiResponse)
async def confirm_plan(request: ConfirmPlanRequest, db: AsyncSession = Depends(get_db)):
    """
    保存/更新旅行计划（用户确认后的结构化数据）
    """
    trip = await crud.get_trip(db, request.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    plan_dict = request.model_dump(exclude={"trip_id"})
    await crud.update_trip(db, request.trip_id, plan=plan_dict, status="confirmed")

    return ApiResponse(
        data={"trip_id": request.trip_id, "plan": plan_dict}
    )


@router.post("/places", response_model=ApiResponse)
async def search_places(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    """
    根据旅行计划搜索推荐地点
    """
    trip = await crud.get_trip(db, request.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    if not trip.plan_json:
        raise HTTPException(status_code=400, detail="请先确认旅行计划")

    # 更新状态为搜索中
    await crud.update_trip(db, request.trip_id, status="searching")

    try:
        # 1. 构建旅行计划对象
        plan = TripPlan(**trip.plan_json)

        # 2. 搜索攻略
        result = await searcher_service.search_places(plan)

        # 3. 为搜索结果补充地图坐标
        city = plan.destination
        all_places = result.attractions + result.restaurants + result.hotels

        for place in all_places:
            if place.latitude is None or place.longitude is None:
                map_point = await mapper_service.search_and_enrich(
                    place_name=place.name,
                    city=city,
                    place_type=place.type.value,
                )
                if map_point:
                    place.latitude = map_point.latitude
                    place.longitude = map_point.longitude
                    if not place.address:
                        place.address = map_point.address

        # 4. 保存地点到数据库
        places_data = [p.model_dump() for p in all_places]
        await crud.batch_add_places(db, request.trip_id, places_data)

        # 5. 更新行程状态和概要
        await crud.update_trip(
            db,
            request.trip_id,
            status="completed",
            summary=result.summary,
        )

        return ApiResponse(data=result.model_dump())

    except Exception as e:
        await crud.update_trip(db, request.trip_id, status="confirmed")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/result/{trip_id}", response_model=ApiResponse)
async def get_search_result(trip_id: str, db: AsyncSession = Depends(get_db)):
    """获取已缓存的搜索结果"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    # 从数据库读取地点
    places = await crud.get_trip_places(db, trip_id)

    # 按类型分组
    attractions = [p for p in places if p.type == "attraction"]
    restaurants = [p for p in places if p.type == "restaurant"]
    hotels = [p for p in places if p.type == "hotel"]

    return ApiResponse(
        data={
            "attractions": [
                {
                    "name": p.name, "type": p.type, "address": p.address,
                    "latitude": p.latitude, "longitude": p.longitude,
                    "rating": p.rating, "description": p.description,
                    "price_range": p.price_range, "opening_hours": p.opening_hours,
                    "tips": p.tips,
                }
                for p in attractions
            ],
            "restaurants": [
                {
                    "name": p.name, "type": p.type, "address": p.address,
                    "latitude": p.latitude, "longitude": p.longitude,
                    "rating": p.rating, "description": p.description,
                    "price_range": p.price_range, "tips": p.tips,
                }
                for p in restaurants
            ],
            "hotels": [
                {
                    "name": p.name, "type": p.type, "address": p.address,
                    "latitude": p.latitude, "longitude": p.longitude,
                    "rating": p.rating, "description": p.description,
                    "price_range": p.price_range, "tips": p.tips,
                }
                for p in hotels
            ],
            "summary": trip.summary,
        }
    )


@router.get("/plan/{trip_id}", response_model=ApiResponse)
async def get_trip_plan(trip_id: str, db: AsyncSession = Depends(get_db)):
    """获取旅行计划"""
    trip = await crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return ApiResponse(data=trip.plan_json)
