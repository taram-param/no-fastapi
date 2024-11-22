from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncSearch

from app.config import settings

ELASTICSEARCH_URL = settings.ELASTICSEARCH_URL


class Search:
    indices = [
        "notes",
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

    async def insert_documents(self, index_name: str, documents: list):
        operations = []
        for index, document in enumerate(documents):
            if index % 1000 == 0:
                await self.es.bulk(operations)
                operations = []
            operations.append({"index": {"_index": index_name}})
            operations.append(document)

        return await self.es.bulk(operations)

    async def reindex(self, index_name: str, documents: list):
        await self.create_index(index_name)
        await self.insert_documents(index_name, documents)

    async def search(self, index_name: str, query: str, fields: list[str]):
        s = AsyncSearch(
            using=self.es,
            index=index_name,
        ).query(
            "multi_match",
            query=query,
            fields=fields,
        )
        result = await s.execute()
        for hit in result:
            # Turn that shit into a document/schema
            pass


es = Search()
