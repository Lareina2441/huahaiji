"""
花海纪 - 地图服务
封装腾讯地图 WebService API
"""
import httpx
from typing import Optional

from app.config import get_settings
from app.models import MapPoint, MapSearchRequest, BatchGeocodeRequest

settings = get_settings()


class MapperService:
    """腾讯地图服务"""

    def __init__(self):
        self.base_url = settings.TENCENT_MAP_BASE_URL
        self.key = settings.TENCENT_MAP_KEY

    async def search_poi(
        self,
        keyword: str,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: int = 50000,
        limit: int = 20,
    ) -> list[MapPoint]:
        """
        POI 地点搜索

        Args:
            keyword: 搜索关键词
            city: 城市名称
            latitude: 中心点纬度
            longitude: 中心点经度
            radius: 搜索半径（米）
            limit: 返回数量限制

        Returns:
            MapPoint 列表
        """
        url = f"{self.base_url}/ws/place/v1/search"
        params = {
            "keyword": keyword,
            "key": self.key,
            "limit": limit,
            "radius": radius,
        }

        if city:
            params["boundary"] = f"region({city},0)"
        if latitude is not None and longitude is not None:
            params["boundary"] = f"nearby({latitude},{longitude},{radius})"
            params["orderby"] = "_distance"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        points = []
        if data.get("status") == 0:
            for item in data.get("data", []):
                location = item.get("location", {})
                points.append(MapPoint(
                    name=item.get("title", ""),
                    address=item.get("address", ""),
                    latitude=location.get("lat", 0),
                    longitude=location.get("lng", 0),
                    place_type=item.get("category", ""),
                    phone=item.get("tel", ""),
                ))

        return points

    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[MapPoint]:
        """
        地理编码：地址 → 经纬度

        Args:
            address: 地址文本
            city: 城市名称（提高精度）

        Returns:
            MapPoint 或 None
        """
        url = f"{self.base_url}/ws/geocoder/v1/"
        params = {
            "address": address,
            "key": self.key,
        }
        if city:
            params["region"] = city

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") == 0:
            result = data.get("result", {})
            location = result.get("location", {})
            return MapPoint(
                name=result.get("title", address),
                address=address,
                latitude=location.get("lat", 0),
                longitude=location.get("lng", 0),
            )

        return None

    async def batch_geocode(
        self,
        addresses: list[str],
        city: Optional[str] = None,
    ) -> list[Optional[MapPoint]]:
        """
        批量地理编码

        Args:
            addresses: 地址列表
            city: 城市名称

        Returns:
            MapPoint 列表（失败的为 None）
        """
        results = []
        for address in addresses:
            try:
                point = await self.geocode(address, city)
                results.append(point)
            except Exception:
                results.append(None)
        return results

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[dict]:
        """
        逆地理编码：经纬度 → 地址

        Returns:
            {"address": "...", "province": "...", "city": "...", "district": "..."}
        """
        url = f"{self.base_url}/ws/geocoder/v1/"
        params = {
            "location": f"{latitude},{longitude}",
            "key": self.key,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") == 0:
            result = data.get("result", {})
            ad_info = result.get("ad_info", {})
            return {
                "address": result.get("address", ""),
                "province": ad_info.get("province", ""),
                "city": ad_info.get("city", ""),
                "district": ad_info.get("district", ""),
            }

        return None

    async def get_direction(
        self,
        from_lat: float,
        from_lng: float,
        to_lat: float,
        to_lng: float,
        mode: str = "driving",
    ) -> Optional[dict]:
        """
        路线规划

        Args:
            from_lat/from_lng: 起点坐标
            to_lat/to_lng: 终点坐标
            mode: 出行方式 driving/walking/transit/bicycling

        Returns:
            {"distance": "12.5km", "duration": "35分钟", "steps": [...]}
        """
        mode_map = {
            "driving": "/ws/direction/v1/driving/",
            "walking": "/ws/direction/v1/walking/",
            "transit": "/ws/direction/v1/transit/",
            "bicycling": "/ws/direction/v1/bicycling/",
        }

        url = f"{self.base_url}{mode_map.get(mode, mode_map['driving'])}"
        params = {
            "from": f"{from_lat},{from_lng}",
            "to": f"{to_lat},{to_lng}",
            "key": self.key,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") == 0:
            routes = data.get("result", {}).get("routes", [])
            if routes:
                route = routes[0]
                return {
                    "distance": route.get("distance", "0"),
                    "duration": route.get("duration", "0"),
                    "steps": [
                        {
                            "instruction": step.get("instruction", ""),
                            "distance": step.get("distance", ""),
                        }
                        for step in route.get("steps", [])[:10]  # 只取前10步
                    ],
                }

        return None

    async def search_and_enrich(
        self,
        place_name: str,
        city: Optional[str] = None,
        place_type: Optional[str] = None,
    ) -> Optional[MapPoint]:
        """
        搜索地点并返回详细信息
        用于将搜索结果中的地点名称映射到地图坐标
        """
        results = await self.search_poi(
            keyword=place_name,
            city=city,
            limit=1,
        )
        if results:
            point = results[0]
            if place_type:
                point.place_type = place_type
            return point
        return None


# 全局服务实例
mapper_service = MapperService()
