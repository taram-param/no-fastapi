from typing import Any
import redis.asyncio as redis
import json

from app.schemas import ExtendedBaseModel

redis_client = redis.Redis(host="redis", decode_responses=True)


class RedisCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> None | Any:
        data = await self.redis_client.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(
        self,
        key: str,
        data: Any,
        schema: ExtendedBaseModel | None = None,
        many: bool = False,
        expiration: int = 60,
    ) -> None:
        serialized_data = self._serialize(data, schema, many)
        await self.redis_client.set(key, serialized_data, ex=expiration)

    def _serialize(
        self,
        data: Any,
        schema: ExtendedBaseModel | None = None,
        many: bool = False,
    ):
        if schema:
            data = (
                [schema.model_validate(item, from_attributes=True).model_dump() for item in data]
                if many
                else schema.model_validate(data, from_attributes=True).model_dump()
            )
        return json.dumps(data)


def get_redis_client():
    return RedisCache(redis_client)
