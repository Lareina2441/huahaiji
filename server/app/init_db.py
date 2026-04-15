"""
花海纪 - 数据库初始化脚本
独立运行，用于创建数据库表
用法: python -m app.init_db
"""
import asyncio
import sys
import os

# 确保能导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, engine
from app.models.database import Base


async def main():
    print("🌸 花海纪 - 数据库初始化")
    print("=" * 40)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 数据库表创建成功！")
    print()
    print("已创建以下表：")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")


if __name__ == "__main__":
    asyncio.run(main())
