from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncSearch

from app.config import settings

ELASTICSEARCH_URL = settings.ELASTICSEARCH_URL


class Search:
    indices = [
        "diary",
    ]

    def __init__(self):
        self.es = AsyncElasticsearch("http://elasticsearch:9200")

    async def info(self):
        client_info = await self.es.info()
        print("Connected to Elasticsearch!")
        print(client_info.body)

    async def create_index(self, index_name: str) -> None:
        await self.es.indices.delete(index=index_name, ignore_unavailable=True)
        await self.es.indices.create(index=index_name)

    async def insert_documents(self, index_name: str, documents: list[dict]):
        operations = []
        for index, document in enumerate(documents):
            if index % 1000 == 0 and index != 0:
                await self.es.bulk(operations=operations)
                operations = []
            operations.append({"index": {"_index": index_name}})
            operations.append(document)

        return await self.es.bulk(operations=operations)

    async def reindex(self, index_name: str, documents: list[dict]):
        await self.create_index(index_name)
        await self.insert_documents(index_name, documents)

    async def search(
        self,
        index_name: str,
        query: str,
        search_fields: list[str],
        filter_fields: dict,
    ):
        s = (
            AsyncSearch(
                using=self.es,
                index=index_name,
            )
            .query(
                "multi_match",
                query=query,
                fields=search_fields,
            )
            .filter("term", **filter_fields)
        )
        response = await s.execute()
        result = []

        for hit in response:
            result.append(hit.to_dict())

        return result


es = Search()
