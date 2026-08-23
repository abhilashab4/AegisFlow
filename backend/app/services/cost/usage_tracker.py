from app.models.usage_log import UsageLog


async def log_usage(
    db,
    username,
    role,
    department,
    model,
    provider,
    prompt_tokens,
    completion_tokens,
    cost,
):
    usage = UsageLog(
        username=username,
        role=role,
        department=department,
        model=model,
        provider=provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=(prompt_tokens + completion_tokens),
        estimated_cost=cost,
    )

    db.add(usage)

    await db.commit()