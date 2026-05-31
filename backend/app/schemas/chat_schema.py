from pydantic import BaseModel


class ChatRequest(BaseModel):

    prompt: str

    task: str = "text-summarization"