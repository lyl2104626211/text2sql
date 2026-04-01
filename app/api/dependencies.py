# ============================================================
# 依赖注入模块 - 提供 FastAPI 路由所需的各类服务依赖
# ============================================================

from app.client.mysql_client_manager import db_meta_manager, db_dw_manager
from app.repositories.es.value_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.client.emdding_client_manager import embedding_manager
from app.services.query_service import QueryService
from fastapi import Depends
from typing import Annotated
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from app.client.es_client_manager import es_manager
from app.client.qdrant_client_manager import qdrant_manager
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


# ----------------------------------------------------------
# Qdrant 矢量数据库依赖
# ----------------------------------------------------------

async def get_column_qdrant_repository():
    """获取 ColumnQdrantRepository 实例，用于检索列信息向量"""
    return ColumnQdrantRepository(qdrant_manager.client)


async def get_metric_qdrant_repository():
    """获取 MetricQdrantRepository 实例，用于检索指标信息向量"""
    return MetricQdrantRepository(qdrant_manager.client)


# ----------------------------------------------------------
# Elasticsearch 依赖
# ----------------------------------------------------------

async def get_value_es_repository():
    """获取 ValueESRepository 实例，用于检索维度值"""
    return ValueESRepository(es_manager.client)


# ----------------------------------------------------------
# MySQL 元数据库依赖
# ----------------------------------------------------------

async def get_meta_mysql_session():
    """获取元数据库（meta）异步会话，每次请求创建新会话"""
    async with db_meta_manager.session_factory() as db_meta_session:
        yield db_meta_session


async def get_meta_mysql_repository(meta_mysql_session: Annotated[AsyncSession, Depends(get_meta_mysql_session)]):
    """获取 MetaMysqlRepository 实例，用于操作元数据库（表结构、指标定义等）"""
    return MetaMysqlRepository(meta_mysql_session)


# ----------------------------------------------------------
# MySQL 数据仓库依赖
# ----------------------------------------------------------

async def get_dw_mysql_session():
    """获取数据仓库（dw）异步会话，每次请求创建新会话"""
    async with db_dw_manager.session_factory() as db_dw_session:
        yield db_dw_session


async def get_dw_mysql_repository(dw_mysql_session: Annotated[AsyncSession, Depends(get_dw_mysql_session)]):
    """获取 DwMysqlRepository 实例，用于执行查询数据仓库的 SQL"""
    return DwMysqlRepository(dw_mysql_session)


# ----------------------------------------------------------
# Embedding 模型依赖
# ----------------------------------------------------------

async def get_embedding_client():
    """获取 HuggingFace Embedding 客户端，用于将文本向量化"""
    return embedding_manager.client


# ----------------------------------------------------------
# 核心 QueryService 依赖
# ----------------------------------------------------------

async def get_query_service(
        column_qdrant_repository: Annotated[ColumnQdrantRepository, Depends(get_column_qdrant_repository)],
        metric_qdrant_repository: Annotated[MetricQdrantRepository, Depends(get_metric_qdrant_repository)],
        value_es_repository: Annotated[ValueESRepository, Depends(get_value_es_repository)],
        meta_mysql_repository: Annotated[MetaMysqlRepository, Depends(get_meta_mysql_repository)],
        dw_mysql_repository: Annotated[DwMysqlRepository, Depends(get_dw_mysql_repository)],
        embedding_client: Annotated[HuggingFaceEndpointEmbeddings, Depends(get_embedding_client)]):
    """获取 QueryService 实例，聚合所有仓储和客户端，是查询流程的核心服务

    依赖关系:
    - column_qdrant_repository: 列向量检索
    - metric_qdrant_repository: 指标向量检索
    - value_es_repository: 维度值检索（Elasticsearch）
    - meta_mysql_repository: 元数据读写（表结构、指标定义）
    - dw_mysql_repository: 数据仓库查询（执行最终 SQL）
    - embedding_client: 文本向量化
    """
    return QueryService(column_qdrant_repository=column_qdrant_repository,
                        embedding_client=embedding_client,
                        metric_qdrant_repository=metric_qdrant_repository,
                        value_es_repository=value_es_repository,
                        meta_mysql_repository=meta_mysql_repository,
                        dw_mysql_repository=dw_mysql_repository)
