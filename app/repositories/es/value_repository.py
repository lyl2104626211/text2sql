from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.service_pojo.value_info_service_pojo import ValueInfo


class ValueESRepository:
    index_name = "value_index"
    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"}
        }
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def ensure_index(self):  # 1 usage
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(
                index=self.index_name,
                mappings=self.index_mappings
            )

    async def upsert(self, value_infos: list[ValueInfo], batch_size=30):

        for i in range(0, len(value_infos), batch_size):
            operations = list()
            batch_value_infos = value_infos[i:i + batch_size]
            for value_info in batch_value_infos:
                operations.append({
                    "index": {
                        "_index": self.index_name
                    }
                })
                operations.append(asdict(value_info))
            await self.client.bulk(operations=operations)

    async def search(self, keyword: str, limit=5, score_threshold=0.6) -> list[ValueInfo]:
        resp = await self.client.search(
            index=self.index_name,
            query={
                "match": {
                    "value": {
                        "query": keyword
                    }
                }
            },
            min_score=score_threshold,
            size=limit
        )
        return [ValueInfo(**hit["_source"]) for hit in resp["hits"]["hits"] if hit["_score"]]
