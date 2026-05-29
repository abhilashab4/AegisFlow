from pydantic import ValidationError

from app.schemas.llm_response_schema import LLMResponseSchema


def validate_llm_response(data: dict):

    try:

        validated = (
            LLMResponseSchema(**data)
        )

        return {
            "valid": True,
            "data": validated.model_dump()
        }

    except ValidationError as e:

        return {
            "valid": False,
            "errors": e.errors()
        }