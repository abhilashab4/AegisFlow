from fastapi import APIRouter, Depends

from app.services.rbac.policy_engine import PolicyEngine
from app.api.dependencies.auth_dependency import get_current_user

router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)

policy_engine = PolicyEngine()


@router.get("/me")
async def get_my_policy(
    current_user=Depends(get_current_user)
):
    department = current_user.department

    return {
        "username": current_user.username,
        "department": department,
        "allowed_tasks": policy_engine.get_allowed_tasks(
            department
        ),
        "rate_limit_per_minute": policy_engine.get_rate_limit(
            department
        )
    }