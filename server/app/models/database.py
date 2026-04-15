"""
花海纪 - 数据库 ORM 模型
SQLAlchemy 异步模型定义
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserModel(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, comment="用户ID")
    openid = Column(String(128), unique=True, nullable=False, comment="微信openid")
    nickname = Column(String(64), default="", comment="昵称")
    avatar = Column(String(512), default="", comment="头像URL")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")


class TripModel(Base):
    """行程表"""
    __tablename__ = "trips"

    id = Column(String(64), primary_key=True, comment="行程ID")
    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    plan_json = Column(JSON, default=dict, comment="旅行计划JSON")
    status = Column(String(20), default="draft", comment="状态: draft/confirmed/searching/completed")
    summary = Column(Text, default="", comment="AI生成的行程概要")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")


class PlaceModel(Base):
    """地点表"""
    __tablename__ = "places"

    id = Column(String(64), primary_key=True, comment="地点ID")
    trip_id = Column(String(64), nullable=False, index=True, comment="行程ID")
    name = Column(String(128), nullable=False, comment="地点名称")
    type = Column(String(20), nullable=False, comment="类型: attraction/restaurant/hotel/transport")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    address = Column(String(256), default="", comment="地址")
    rating = Column(Float, default=0, comment="评分")
    description = Column(Text, default="", comment="简介")
    opening_hours = Column(String(128), default="", comment="营业时间")
    price_range = Column(String(64), default="", comment="价格范围")
    image_url = Column(String(512), default="", comment="图片URL")
    tips = Column(Text, default="", comment="攻略/小贴士")
    sort_order = Column(Integer, default=0, comment="排序权重")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")


class ChatMessageModel(Base):
    """聊天记录表"""
    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True, comment="消息ID")
    trip_id = Column(String(64), nullable=False, index=True, comment="行程ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
