import asyncio

from elasticsearch import AsyncElasticsearch
from app.config.app_config import ESConfig, app_config


class EsClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: AsyncElasticsearch | None = None

    def _geturl(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(hosts=[self._geturl()])

    async def close(self):
        await self.client.close()


es_manager = EsClientManager(config=app_config.es)
if __name__ == '__main__':
    async def test():
        # await es_client.indices.create(
        #     index="books",
        # )
        # resp = await es_client.index(
        #     index="books",
        #     document={
        #         "name": "Snow Crash",
        #         "author": "Neal Stephenson",
        #         "release_date": "1992-06-01",
        #         "page_count": 470
        #     },
        # )
        # print(resp)
        res = await  es_client.search(
            index="books",
            query={
                "match": {
                    "name": "Snow"
                }
            }
        )
        await es_client.close()
        print(res)



    asyncio.run(test())

