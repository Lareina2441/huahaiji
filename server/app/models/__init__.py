"""
花海纪 - 数据模型模块
包含 Pydantic 请求/响应模型 和 SQLAlchemy ORM 模型
"""

# ============================================================
# Pydantic 数据模型（请求/响应）
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ---------- 枚举类型 ----------

class PlaceType(str, Enum):
    """地点类型"""
    ATTRACTION = "attraction"  # 景点
    RESTAURANT = "restaurant"  # 餐厅
    HOTEL = "hotel"           # 酒店
    TRANSPORT = "transport"    # 交通枢纽


class TripStatus(str, Enum):
    """行程状态"""
    DRAFT = "draft"            # 草稿（对话中）
    CONFIRMED = "confirmed"    # 已确认
    SEARCHING = "searching"    # 搜索中
    COMPLETED = "completed"    # 已完成


# ---------- 聊天相关 ----------

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user / assistant / system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    trip_id: Optional[str] = Field(None, description="行程ID，为空则创建新行程")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str = Field(..., description="AI 回复内容")
    trip_id: str = Field(..., description="行程ID")
    is_info_complete: bool = Field(False, description="信息是否收集完整")


class ExtractRequest(BaseModel):
    """信息抽取请求"""
    trip_id: str = Field(..., description="行程ID")


# ---------- 旅行计划 ----------

class TripPlan(BaseModel):
    """结构化旅行计划"""
    people_count: Optional[str] = Field(None, description="出行人数")
    people_type: Optional[str] = Field(None, description="人群类型: 家庭/情侣/朋友/独自")
    budget: Optional[str] = Field(None, description="预算范围")
    days: Optional[str] = Field(None, description="出行天数")
    destination: Optional[str] = Field(None, description="目的地")
    dates: Optional[str] = Field(None, description="出行日期")
    accommodation_preference: Optional[str] = Field(None, description="住宿偏好")
    food_preference: Optional[str] = Field(None, description="饮食偏好")
    transport_preference: Optional[str] = Field(None, description="交通偏好")
    special_needs: Optional[str] = Field(None, description="特殊需求")
    interests: Optional[str] = Field(None, description="兴趣偏好")
    confidence: float = Field(0.0, description="信息完整度 0-1")


class TripPlanConfirm(BaseModel):
    """旅行计划确认请求"""
    trip_id: str = Field(..., description="行程ID")
    plan: TripPlan = Field(..., description="确认后的旅行计划")


# ---------- 搜索结果 ----------

class PlaceInfo(BaseModel):
    """地点信息"""
    name: str = Field(..., description="地点名称")
    type: PlaceType = Field(..., description="地点类型")
    address: Optional[str] = Field(None, description="地址")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    rating: Optional[float] = Field(None, description="评分")
    description: Optional[str] = Field(None, description="简介")
    price_range: Optional[str] = Field(None, description="价格范围")
    opening_hours: Optional[str] = Field(None, description="营业时间")
    image_url: Optional[str] = Field(None, description="图片URL")
    tips: Optional[str] = Field(None, description="攻略/小贴士")
    sort_order: int = Field(0, description="排序权重")


class SearchResult(BaseModel):
    """搜索结果"""
    attractions: list[PlaceInfo] = Field(default_factory=list, description="景点列表")
    restaurants: list[PlaceInfo] = Field(default_factory=list, description="餐厅列表")
    hotels: list[PlaceInfo] = Field(default_factory=list, description="酒店列表")
    summary: Optional[str] = Field(None, description="AI 生成的行程概要")


class SearchRequest(BaseModel):
    """搜索请求"""
    trip_id: str = Field(..., description="行程ID")


# ---------- 地图相关 ----------

class MapSearchRequest(BaseModel):
    """地图搜索请求"""
    keyword: str = Field(..., description="搜索关键词")
    city: Optional[str] = Field(None, description="城市")
    latitude: Optional[float] = Field(None, description="中心点纬度")
    longitude: Optional[float] = Field(None, description="中心点经度")
    radius: int = Field(50000, description="搜索半径(米)")


class MapPoint(BaseModel):
    """地图点"""
    name: str
    address: str
    latitude: float
    longitude: float
    place_type: Optional[str] = None
    phone: Optional[str] = None


class BatchGeocodeRequest(BaseModel):
    """批量地理编码请求"""
    addresses: list[str] = Field(..., description="地址列表")
    city: Optional[str] = Field(None, description="城市")


# ---------- 行程管理 ----------

class TripCreate(BaseModel):
    """创建行程"""
    user_id: str = Field(..., description="用户ID")


class TripUpdate(BaseModel):
    """更新行程"""
    plan: Optional[TripPlan] = None
    status: Optional[TripStatus] = None
    places: Optional[list[PlaceInfo]] = None


# ---------- 统一响应 ----------

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = Field(0, description="状态码, 0=成功")
    data: Optional[dict | list | str] = Field(None, description="响应数据")
    msg: str = Field("success", description="提示信息")
