from starlette.responses import StreamingResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from typing import Annotated

from app.services.query_service import QueryService

query_router = APIRouter()


@query_router.post("/api/query")
async def query_handler(query: QuerySchema, query_service: Annotated[QueryService, Depends(get_query_service)]):
    return StreamingResponse(
        query_service.query(query.query),  # 一个异步生成器
        media_type="text/event-stream"  # 指定内容类型
    )
