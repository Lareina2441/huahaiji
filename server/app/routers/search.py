"""
花海纪 - 搜索路由
处理旅行攻略搜索相关接口
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models import SearchRequest, ApiResponse, TripPlan, SearchResult
from app.services.searcher import searcher_service
from app.services.mapper import mapper_service

router = APIRouter()

# 内存存储：trip_id -> 搜索结果
_search_store: dict[str, dict] = {}
# 内存存储：trip_id -> TripPlan
_plan_store: dict[str, TripPlan] = {}


@router.post("/places", response_model=ApiResponse)
async def search_places(request: SearchRequest):
    """
    根据旅行计划搜索推荐地点
    """
    plan = _plan_store.get(request.trip_id)
    if not plan:
        raise HTTPException(status_code=404, detail="未找到旅行计划，请先确认旅行信息")

    try:
        # 1. 搜索攻略
        result = await searcher_service.search_places(plan)

        # 2. 为搜索结果补充地图坐标
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

        # 3. 存储结果
        _search_store[request.trip_id] = result.model_dump()

        return ApiResponse(data=result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/confirm-plan", response_model=ApiResponse)
async def confirm_plan(trip_id: str, plan: TripPlan):
    """
    保存/更新旅行计划（用户确认后的结构化数据）
    """
    _plan_store[trip_id] = plan
    return ApiResponse(data={"trip_id": trip_id, "plan": plan.model_dump()})


@router.get("/result/{trip_id}", response_model=ApiResponse)
async def get_search_result(trip_id: str):
    """获取已缓存的搜索结果"""
    result = _search_store.get(trip_id)
    if not result:
        raise HTTPException(status_code=404, detail="未找到搜索结果，请先执行搜索")
    return ApiResponse(data=result)


@router.get("/plan/{trip_id}", response_model=ApiResponse)
async def get_trip_plan(trip_id: str):
    """获取旅行计划"""
    plan = _plan_store.get(trip_id)
    if not plan:
        raise HTTPException(status_code=404, detail="未找到旅行计划")
    return ApiResponse(data=plan.model_dump())
