# test_redis.py

import asyncio
from app.db.redis import redis_client

async def main():

    try:
        print("Testing Redis...")

        pong = await redis_client.ping()

        print("PING:", pong)

        await redis_client.set(
            "hello",
            "world"
        )

        value = await redis_client.get(
            "hello"
        )

        print("VALUE:", value)

    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())