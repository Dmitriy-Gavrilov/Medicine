from redis.asyncio import Redis


class RedisService:
    def __init__(self):
        self.redis_client = Redis(host="localhost",
                                  port=6379,
                                  decode_responses=True)


redisService = RedisService()
