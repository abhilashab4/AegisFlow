from pydantic import BaseModel


class LLMResponseSchema(BaseModel):

    status: str
    response: str
    model: str