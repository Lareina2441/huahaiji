"""
花海纪 - 后端服务层初始化
"""
from app.services.deepseek import deepseek_service
from app.services.extractor import extractor_service
from app.services.searcher import searcher_service
from app.services.mapper import mapper_service

__all__ = [
    "deepseek_service",
    "extractor_service",
    "searcher_service",
    "mapper_service",
]
