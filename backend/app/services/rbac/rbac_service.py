from app.services.rbac.policy_engine import PolicyEngine

policy_engine = PolicyEngine()


def check_access(user_context, endpoint: str, model: str):

    allowed, reason = policy_engine.is_allowed(
        role=user_context.role,
        endpoint=endpoint,
        model=model
    )

    return {
        "allowed": allowed,
        "reason": reason
    }