import json

from app.agent.context import DataAgentContext
from app.agent.graph import graph_compile
from app.agent.state import DataAgentState
from app.repositories.es.value_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from app.core.log import logger


class QueryService:
    def __init__(self, column_qdrant_repository: ColumnQdrantRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 value_es_repository: ValueESRepository,
                 meta_mysql_repository: MetaMysqlRepository,
                 dw_mysql_repository: DwMysqlRepository,
                 embedding_client: HuggingFaceEndpointEmbeddings):
        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.embedding_client = embedding_client

    async def query(self, query):
        """执行查询，返回流式结果

        Args:
            query: 用户查询文本
        Yields:
            chunk: LangGraph 流式输出的结果块
        """
        state = DataAgentState(query=query)
        context = DataAgentContext(column_qdrant_repository=self.column_qdrant_repository,
                                   embedding_model=self.embedding_client,
                                   metric_qdrant_repository=self.metric_qdrant_repository,
                                   value_es_repository=self.value_es_repository,
                                   meta_mysql_repository=self.meta_mysql_repository,
                                   dw_mysql_repository=self.dw_mysql_repository)

        try:
            async for chunk in graph_compile.astream(input=state, context=context, stream_mode="custom"):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"  # SSE格式发送数据
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n"

