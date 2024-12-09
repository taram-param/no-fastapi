from elasticsearch_dsl import AsyncDocument, Date, Integer, Keyword, Text, async_connections

from app.elastic import es

async_connections.add_connection("default", es.es)


class Note(AsyncDocument):
    title = Text(analyzer="snowball", fields={"raw": Keyword})
    content = Text(analyzer="snowball")
    created_at = Date()
    diary_id = Integer(required=True)
    user_id = Integer(required=True)

    class Index:
        name = "diary"
        settings = {
            "number_of_shards": 1,
        }
