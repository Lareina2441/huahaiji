"""
花海纪 - 后端配置模块
使用 pydantic-settings 管理环境变量
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "花海纪"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/huahaiji"
    REDIS_URL: str = "redis://localhost:6379/0"

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 2048
    DEEPSEEK_TEMPERATURE: float = 0.7

    # 腾讯地图 API 配置
    TENCENT_MAP_KEY: str = ""
    TENCENT_MAP_BASE_URL: str = "https://apis.map.qq.com"

    # 搜索 API 配置 (Serper)
    SERPER_API_KEY: str = ""
    SERPER_BASE_URL: str = "https://google.serper.dev"

    # 微信小程序配置
    WX_APP_ID: str = ""
    WX_APP_SECRET: str = ""

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]

    # 对话配置
    MAX_CONTEXT_ROUNDS: int = 10  # 最大上下文轮数

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置单例"""
    return Settings()
