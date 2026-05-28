from pydantic import BaseModel


class PIITestRequest(BaseModel):
    text: str