import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.client.mysql_client_manager import db_meta_manager, db_dw_manager
from app.client.es_client_manager import es_manager
from app.client.qdrant_client_manager import qdrant_manager
from app.client.emdding_client_manager import embedding_manager


# ----------------------------------------------------------
# 应用生命周期管理 - 初始化/关闭所有客户端
# ----------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器

    - 启动时：依次初始化所有客户端（MySQL、ES、Qdrant、Embedding）
    - 关闭时：依次关闭所有客户端，释放资源
    """
    # ---- 启动阶段：初始化所有客户端 ----
    db_meta_manager.init()
    db_dw_manager.init()
    es_manager.init()
    qdrant_manager.init()
    embedding_manager.init()

    yield  # 应用运行中

    # ---- 关闭阶段：释放所有客户端资源 ----
    await asyncio.gather(
        db_meta_manager.close(),
        db_dw_manager.close(),
        es_manager.close(),
        qdrant_manager.close(),
    )
