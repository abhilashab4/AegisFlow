from app.services.rbac.policy_engine import (
    PolicyEngine
)

policy_engine = PolicyEngine()


def check_access(
    user_context,
    endpoint: str,
    task: str
):

    allowed, reason, model = (
        policy_engine.is_allowed(
            role=user_context.role,
            endpoint=endpoint,
            task=task
        )
    )

    return {
        "allowed": allowed,
        "reason": reason,
        "model": model
    }