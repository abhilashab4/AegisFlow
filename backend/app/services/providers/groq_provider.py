
from groq import AsyncGroq

from app.core.config import settings

from app.services.providers.base_provider import (
    BaseLLMProvider
)


class GroqProvider(
    BaseLLMProvider
):

    def __init__(self):

        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = (
            "llama-3.1-8b-instant"
        )

    async def generate(
        self,
        prompt: str
    ):

        response = await (
            self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are an enterprise AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.3
            )
        )

        return (
            response
            .choices[0]
            .message.content
        )


    async def stream_generate(
        self,
        prompt: str
    ):

        stream = await (
            self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are an enterprise AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.3,

                stream=True
            )
        )

        async for chunk in stream:

            delta = (
                chunk.choices[0]
                .delta.content
            )

            if delta:
                yield delta