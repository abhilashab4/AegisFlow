from app.db.redis import redis_client

from app.services.rbac.policy_engine import (
    PolicyEngine
)

policy_engine = PolicyEngine()


async def check_rate_limit(
    username: str,
    department: str
):

    limit = (
        policy_engine.get_rate_limit(
            department
        )
    )

    key = f"rate_limit:{username}"

    current_count = await redis_client.incr(
        key
    )

    if current_count == 1:

        await redis_client.expire(
            key,
            60
        )

    return current_count <= limit