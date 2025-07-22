import json

from redis.asyncio import Redis

from app.schemas.base import BaseSchema
from app.settings import settings


class RedisService:
    def __init__(self):
        self.redis_client = Redis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT,
                                  password=settings.REDIS_PASSWORD,
                                  max_connections=100,
                                  decode_responses=True)

    async def set_cache(self, key: str, value: BaseSchema, ex: int) -> None:
        json_value = json.dumps(value, default=lambda v: v.model_dump(mode="json"))
        await self.redis_client.set(f"cache:{key}", json_value, ex=ex)

    async def get_cache(self, key: str):
        value = await self.redis_client.get(f"cache:{key}")
        if value:
            return json.loads(value)
        return None

    async def del_cache(self, key: str) -> None:
        await self.redis_client.delete(f"cache:{key}")


redisService = RedisService()
