import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies.auth_dependency import get_current_user
from app.schemas.chat_schema import ChatRequest
from app.schemas.auth_schema import UserContext
from app.services.pii_service import sanitize_text
from app.services.llm_service import generate_llm_response
from app.services.guardrail_service import check_output_guardrails
from app.services.audit_logger import log_request

router = APIRouter(prefix="/ai", tags=["AI Gateway"])

@router.post("/generate")
async def generate(
    data: ChatRequest,
    current_user: UserContext = Depends(get_current_user)
):
    request_id = str(uuid.uuid4())
    sanitized_prompt = None 
    
    log_base = {
        "request_id": request_id,
        "username": current_user.username,
        "role": current_user.role,
        "dept": current_user.dept,
        "original_prompt": data.prompt
    }

    try:
        pii_input = await sanitize_text(data.prompt)
        sanitized_prompt = pii_input["sanitized_text"]

        llm_response = await generate_llm_response(sanitized_prompt)

        pii_output = await sanitize_text(llm_response)
        final_response = pii_output["sanitized_text"]

        guard_result = await check_output_guardrails(final_response)

        if not guard_result["safe"]:
            await log_request({**log_base, "blocked": True, "reason": guard_result["reason"]})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Compliance Violation: {guard_result['reason']}"
            )

        await log_request({**log_base,"sanitized_prompt": sanitized_prompt, "blocked": False, "status": "success"})

        return {
            "request_id": request_id,
            "response": final_response,
            "sanitized_prompt": sanitized_prompt
        }

    except Exception as e:
        await log_request({**log_base, "sanitized_prompt": sanitized_prompt, "error": str(e), "status": "system_failure"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal gateway processing error"
        )