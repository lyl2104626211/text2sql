from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config.app_config import app_config
from qdrant_client.models import PointStruct
from app.service_pojo.column_service_pojo import ColumnServicePOJO


class ColumnQdrantRepository:
    collection_name = "column_info_collection"
    batch_size = 20

    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.qdrant_client = qdrant_client

    async def build_index(self):
        if not await self.qdrant_client.collection_exists("column_info_collection"):
            await self.qdrant_client.create_collection(
                collection_name="column_info_collection",
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE),
            )

    async def upsert(self, ids: list[str], embeddings_values: list[list[float]], payloads: list[dict]):
        points_struct = [PointStruct(id=id, vector=embedding_values, payload=payload) for id, embedding_values, payload
                         in zip(ids, embeddings_values, payloads)]
        for i in range(0, len(points_struct), self.batch_size):
            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points_struct[i:i + self.batch_size]
            )

    async def search(self, query_vector: list[float], score_threshold=0.6, limit: int = 20) -> list[ColumnServicePOJO]:
        result = await self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return [ColumnServicePOJO(**point.payload) for point in result.points]
