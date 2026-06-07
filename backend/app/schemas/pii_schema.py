from pydantic import BaseModel


class PIITestRequest(BaseModel):
    text: str
    

class PIIPreviewRequest(
    BaseModel
):

    prompt: str