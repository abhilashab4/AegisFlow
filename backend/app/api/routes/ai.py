import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import traceback

from app.services.guardrails.output_guardrail import OutputGuardrail
from app.services.guardrails.embedding_service import EmbeddingService
from app.services.guardrails.policy_service import PolicyService

from app.api.dependencies.auth_dependency import get_current_user
from app.schemas.chat_schema import ChatRequest
from app.schemas.auth_schema import UserContext
from app.db.session import AsyncSessionLocal

from app.services.pii.pii_service import PIIPipeline
from app.services.providers.provider_router import ProviderRouter
from app.services.schema_validator import validate_llm_response
from app.services.audits.audit_logger import AuditLogger
from app.services.rbac.rbac_service import check_access
# from app.services.streaming.stream_llm_service import stream_llm_response
from app.services.cost.cost_calculator import estimate_cost
from app.services.cost.usage_tracker import log_usage
from app.services.rate_limit.rate_limit_service import (
    check_rate_limit
)
from app.schemas.pii_schema import (
    PIIPreviewRequest, PIITestRequest
)
router = APIRouter(prefix="/ai", tags=["AI Gateway"])

provider_router = ProviderRouter()
audit_logger = AuditLogger()
pii_pipeline = PIIPipeline()


def _verify_and_sanitize_pii(prompt: str, current_user: UserContext, log_base: Dict[str, Any]) -> str:
    pii_result = pii_pipeline.sanitize_prompt(prompt)
    if not pii_result["safe"]:
        audit_logger.log_event(
            event_type="PII_VERIFICATION_FAILURE",
            actor=current_user.username,
            metadata={**log_base, "reason": pii_result["reason"]}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pii_result["reason"]
        )
    return pii_result["sanitized_text"]


def _verify_rbac_access(current_user: UserContext, endpoint: str, task: str, log_base: Dict[str, Any]) -> Dict[str, Any]:
    rbac_result = check_access(
        user_context=current_user,
        endpoint=endpoint,
        task=task
    )
    if not rbac_result["allowed"]:
        audit_logger.log_event(
            event_type="RBAC_BLOCK",
            actor=current_user.username,
            metadata={**log_base, "reason": rbac_result["reason"]}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {rbac_result['reason']}"
        )
    return rbac_result


async def _validate_output_guardrails(
    llm_response: str,
    current_user: UserContext,
    log_base: Dict[str, Any]
) -> None:

    async with AsyncSessionLocal() as db:

        embedding_service = EmbeddingService()

        policy_service = PolicyService(
            db=db,
            embedding_service=embedding_service
        )

        guardrail = OutputGuardrail(
            policy_service=policy_service
        )

        guard_result = await guardrail.validate(
            llm_response
        )
        
        guard_result = await guardrail.validate(llm_response)

        print("\n" + "=" * 60)
        print("OUTPUT GUARDRAIL RESULT")
        print("=" * 60)
        print("LLM RESPONSE:")
        print(llm_response)
        print("\nGUARD RESULT:")
        print(guard_result)
        print("=" * 60)

    if not guard_result["safe"]:

        audit_logger.log_event(
            event_type="POLICY_VIOLATION",
            actor=current_user.username,
            metadata={
                **log_base,
                "blocked": True,
                "category": guard_result.get("category"),
                "risk_score": guard_result.get("risk_score"),
                "reason": guard_result.get("reason")
            }
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": guard_result.get(
                    "replacement",
                    "Response blocked by corporate compliance policy."
                ),
                "category": guard_result.get("category"),
                "risk_score": guard_result.get("risk_score")
            }
        )


def _validate_response_schema(structured_response: Dict[str, Any], current_user: UserContext, log_base: Dict[str, Any]) -> None:
    schema_result = validate_llm_response(structured_response)
    if not schema_result["valid"]:
        audit_logger.log_event(
            event_type="SCHEMA_FAILURE",
            actor=current_user.username,
            metadata={**log_base, "errors": schema_result["errors"]}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schema validation failed"
        )


async def _verify_rate_limit(current_user: UserContext, log_base: Dict[str, Any]) -> None:
    allowed = await check_rate_limit(
        username=current_user.username,
        department=current_user.department
    )

    if not allowed:
        audit_logger.log_event(
            event_type="RATE_LIMIT_BLOCK",
            actor=current_user.username,
            metadata=log_base
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Rate limit exceeded. "
                "Please try again later."
            )
        )

@router.post("/preview-sanitization")
async def preview_sanitization(
    data: PIIPreviewRequest,
    current_user: UserContext = Depends(get_current_user)
):

    result = pii_pipeline.sanitize_prompt(data.prompt)

    return {
        "safe": result["safe"],
        "original_prompt": data.prompt,
        "sanitized_prompt": result["sanitized_text"],
        "reason": result.get("reason"),
        "residual_pii": result.get("residual_pii", []),
    }
    
@router.post("/generate")
async def generate(
    data: ChatRequest,
    current_user: UserContext = Depends(get_current_user)
):
    request_id = str(uuid.uuid4())
    log_base = {
        "request_id": request_id,
        "username": current_user.username,
        "role": current_user.role,
        "department": current_user.department,
        "original_prompt": data.prompt
    }

    try:
        await _verify_rate_limit(current_user, log_base)
        sanitized_prompt = _verify_and_sanitize_pii(data.prompt, current_user, log_base)
        rbac_result = _verify_rbac_access(current_user, "/ai/generate", data.task, log_base)
        
        selected_model = rbac_result["model"]
        provider_name = provider_router.resolve_provider(selected_model)
        print(f"DEBUG: Selected Model = {selected_model}")

        llm_response = await provider_router.generate(
            prompt=sanitized_prompt,
            model=selected_model
        )

        prompt_tokens = len(sanitized_prompt.split())
        completion_tokens = len(llm_response.split())
        cost = estimate_cost(
            model=selected_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )

        await _validate_output_guardrails(llm_response, current_user, log_base)

        structured_response = {
            "status": "success",
            "response": llm_response,
            "model": "llama-3.1-8b-instant"
        }
        
        async with AsyncSessionLocal() as db:
            await log_usage(
                db=db,
                username=current_user.username,
                role=current_user.role,
                department=current_user.department,
                model=selected_model,
                provider=provider_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost
            )

        _validate_response_schema(structured_response, current_user, log_base)

        audit_logger.log_event(
            event_type="LLM_REQUEST",
            actor=current_user.username,
            metadata={
                **log_base,
                "sanitized_prompt": sanitized_prompt,
                "blocked": False
            }
        )

        return {
            "request_id": request_id,
            "status": "success",
            "model": selected_model,
            "provider": provider_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost": cost,
            "sanitized_prompt": sanitized_prompt,
            "response": llm_response
        }

    except HTTPException as http_error:
        raise http_error


    except Exception as e:

        print("\n" + "=" * 50)
        print("FULL ERROR")
        print("=" * 50)

        traceback.print_exc()

        print("=" * 50)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# @router.post("/generate-stream")
# async def generate_stream(
#     data: ChatRequest,
#     current_user: UserContext = Depends(get_current_user)
# ):
#     log_context = {"username": current_user.username}

#     await _verify_rate_limit(current_user, log_context)
#     sanitized_prompt = _verify_and_sanitize_pii(data.prompt, current_user, log_context)
#     rbac_result = _verify_rbac_access(current_user, "/ai/generate-stream", data.task, log_context)

#     return StreamingResponse(
#         stream_llm_response(
#             sanitized_prompt,
#             rbac_result["model"]
#         ),
#         media_type="text/plain"
#     )