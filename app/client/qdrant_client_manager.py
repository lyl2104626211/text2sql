import asyncio


from qdrant_client import AsyncQdrantClient
from app.config.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: AsyncQdrantClient | None = None

    def _geturl(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url=self._geturl())

    async def close(self):
        await self.client.close()


qdrant_manager = QdrantClientManager(config=app_config.qdrant)
if __name__ == '__main__':
    client = qdrant_manager.client


    async def test():
        search_result = (await client.query_points(
            collection_name="test_collection",
            query=[0.2, 0.1, 0.9, 0.7],
            with_payload=False,
            limit=3
        )).points

        print(search_result)


    asyncio.run(test())
