"""
花海纪 - 地图路由
处理地图搜索、地理编码、路线规划相关接口
"""
from fastapi import APIRouter, HTTPException

from app.models import (
    MapSearchRequest, MapPoint, BatchGeocodeRequest, ApiResponse,
)
from app.services.mapper import mapper_service

router = APIRouter()


@router.get("/search", response_model=ApiResponse)
async def search_map_places(
    keyword: str,
    city: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = 50000,
    limit: int = 20,
):
    """
    搜索地图地点（POI）
    """
    try:
        points = await mapper_service.search_poi(
            keyword=keyword,
            city=city,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            limit=limit,
        )
        return ApiResponse(
            data=[p.model_dump() for p in points]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"地图搜索失败: {str(e)}")


@router.post("/geocode", response_model=ApiResponse)
async def geocode_address(address: str, city: str | None = None):
    """
    地理编码：地址 → 经纬度
    """
    point = await mapper_service.geocode(address, city)
    if not point:
        raise HTTPException(status_code=404, detail="未找到对应地址")
    return ApiResponse(data=point.model_dump())


@router.post("/batch-geocode", response_model=ApiResponse)
async def batch_geocode(request: BatchGeocodeRequest):
    """
    批量地理编码
    """
    results = await mapper_service.batch_geocode(
        addresses=request.addresses,
        city=request.city,
    )
    return ApiResponse(
        data=[p.model_dump() if p else None for p in results]
    )


@router.get("/reverse-geocode", response_model=ApiResponse)
async def reverse_geocode(latitude: float, longitude: float):
    """
    逆地理编码：经纬度 → 地址
    """
    result = await mapper_service.reverse_geocode(latitude, longitude)
    if not result:
        raise HTTPException(status_code=404, detail="逆地理编码失败")
    return ApiResponse(data=result)


@router.get("/direction", response_model=ApiResponse)
async def get_direction(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
    mode: str = "driving",
):
    """
    路线规划
    mode: driving / walking / transit / bicycling
    """
    result = await mapper_service.get_direction(
        from_lat=from_lat,
        from_lng=from_lng,
        to_lat=to_lat,
        to_lng=to_lng,
        mode=mode,
    )
    if not result:
        raise HTTPException(status_code=404, detail="路线规划失败")
    return ApiResponse(data=result)
