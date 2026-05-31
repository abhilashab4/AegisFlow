import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.api.dependencies.auth_dependency import (
    get_current_user
)

from app.schemas.chat_schema import (
    ChatRequest
)

from app.schemas.auth_schema import (
    UserContext
)

from app.services.pii.pii_service import (
    PIIPipeline
)

from app.services.providers.provider_router import (
    ProviderRouter
)

from app.services.guardrails.output_guardrail import (
    OutputGuardrail
)

from app.services.schema_validator import (
    validate_llm_response
)

from app.services.audits.audit_logger import (
    AuditLogger
)

from app.services.rbac.rbac_service import (
    check_access
)

from fastapi.responses import (
    StreamingResponse
)

from app.services.streaming.stream_llm_service import (
    stream_llm_response
)



router = APIRouter(
    prefix="/ai",
    tags=["AI Gateway"]
)


provider_router = ProviderRouter()

guardrail = OutputGuardrail()

audit_logger = AuditLogger()

pii_pipeline = PIIPipeline()


@router.post("/generate")
async def generate(
    data: ChatRequest,
    current_user: UserContext = Depends(
        get_current_user
    )
):

    request_id = str(uuid.uuid4())

    sanitized_prompt = None

    log_base = {

        "request_id":
            request_id,

        "username":
            current_user.username,

        "role":
            current_user.role,

        "department":
            current_user.dept,

        "original_prompt":
            data.prompt
    }

    try:


        pii_result = (
            pii_pipeline.sanitize_prompt(
                data.prompt
            )
        )


        if not pii_result["safe"]:

            audit_logger.log_event(

                event_type=
                    "PII_VERIFICATION_FAILURE",

                actor=
                    current_user.username,

                metadata={
                    **log_base,
                    "reason":
                        pii_result["reason"]
                }
            )

            raise HTTPException(

                status_code=
                    status.HTTP_400_BAD_REQUEST,

                detail=
                    pii_result["reason"]
            )

        sanitized_prompt = (
            pii_result["sanitized_text"]
        )


        #RBAC check
        rbac_result = check_access(
            user_context=current_user,
            endpoint="/ai/generate",
            model="llama-3.1-8b-instant"
        )

        if not rbac_result["allowed"]:

            audit_logger.log_event(
                event_type="RBAC_BLOCK",
                actor=current_user.username,
                metadata={
                    **log_base,
                    "reason": rbac_result["reason"]
                }
            )

            raise HTTPException(
                status_code=403,
                detail=f"Access denied: {rbac_result['reason']}"
            )


        #LLM call
        llm_response = await (
            provider_router.generate(
                prompt=sanitized_prompt
            )
        )

        guard_result = (
            guardrail.validate(
                llm_response
            )
        )

        if not guard_result["safe"]:

            audit_logger.log_event(

                event_type=
                    "POLICY_VIOLATION",

                actor=
                    current_user.username,

                metadata={
                    **log_base,
                    "blocked": True,
                    "reason":
                        guard_result[
                            "reason"
                        ]
                }
            )

            raise HTTPException(

                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "Compliance violation: "
                    f"{guard_result['reason']}"
                )
            )


        structured_response = {

            "status":
                "success",

            "response":
                llm_response,

            "model":
                "llama-3.1-8b-instant"
        }

        schema_result = (
            validate_llm_response(
                structured_response
            )
        )

        if not schema_result["valid"]:

            audit_logger.log_event(

                event_type=
                    "SCHEMA_FAILURE",

                actor=
                    current_user.username,

                metadata={
                    **log_base,
                    "errors":
                        schema_result[
                            "errors"
                        ]
                }
            )

            raise HTTPException(

                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=
                    "Schema validation failed"
            )

        audit_logger.log_event(

            event_type=
                "LLM_REQUEST",

            actor=
                current_user.username,

            metadata={
                **log_base,

                "sanitized_prompt":
                    sanitized_prompt,

                "blocked":
                    False
            }
        )


        final_response = {

            "request_id":
                request_id,

            "status":
                "success",

            "sanitized_prompt":
                sanitized_prompt,

            "response":
                llm_response
        }

        return final_response


    except HTTPException as http_error:

        raise


    except Exception as e:

        audit_logger.log_event(

            event_type=
                "SYSTEM_FAILURE",

            actor=
                current_user.username,

            metadata={
                **log_base,
                "error": str(e)
            }
        )

        raise HTTPException(

            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Internal gateway error"
        )
    

@router.post("/generate-stream")
async def generate_stream(

    data: ChatRequest,

    current_user: UserContext = Depends(
        get_current_user
    )
):


    pii_result = (
        pii_pipeline.sanitize_prompt(
            data.prompt
        )
    )

    if not pii_result["safe"]:

        raise HTTPException(

            status_code=400,

            detail=
                pii_result["reason"]
        )

    sanitized_prompt = (
        pii_result["sanitized_text"]
    )


    rbac_result = check_access(

        user_context=current_user,

        endpoint="/ai/generate-stream",

        model="llama-3.1-8b-instant"
    )

    if not rbac_result["allowed"]:

        raise HTTPException(

            status_code=403,

            detail=
                rbac_result["reason"]
        )

    return StreamingResponse(

        stream_llm_response(
            sanitized_prompt
        ),

        media_type=
            "text/plain"
    )