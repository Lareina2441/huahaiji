"""
花海纪 - FastAPI 应用入口
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, close_db

# 导入路由
from app.routers import chat, search, map, trip

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化数据库，关闭时释放连接"""
    # 启动
    await init_db()
    yield
    # 关闭
    await close_db()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="花海纪 - AI 智能旅行规划助手后端服务",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ---------- 中间件 ----------

    # CORS 跨域配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- 全局异常处理 ----------

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常捕获"""
        return JSONResponse(
            status_code=500,
            content={
                "code": -1,
                "data": None,
                "msg": f"服务器内部错误: {str(exc)}",
            },
        )

    # ---------- 注册路由 ----------

    app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
    app.include_router(search.router, prefix="/api/search", tags=["搜索"])
    app.include_router(map.router, prefix="/api/map", tags=["地图"])
    app.include_router(trip.router, prefix="/api/trip", tags=["行程"])

    # ---------- 健康检查 ----------

    @app.get("/health", tags=["系统"])
    async def health_check():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    @app.get("/", tags=["系统"])
    async def root():
        return {"message": "🌸 花海纪 API 服务运行中", "docs": "/docs"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
