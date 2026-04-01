from typing import TypedDict

from app.repositories.es.value_repository import ValueESRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository: ColumnQdrantRepository
    embedding_model: HuggingFaceEndpointEmbeddings
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
    meta_mysql_repository: MetaMysqlRepository
    dw_mysql_repository: DwMysqlRepository
