from app.services.providers.base_provider import (
    BaseLLMProvider
)


class OpenAIProvider(
    BaseLLMProvider
):

    async def generate(
        self,
        prompt: str,
        model: str
    ):

        raise NotImplementedError(
            "OpenAI provider not configured"
        )

    async def stream_generate(
        self,
        prompt: str,
        model: str
    ):

        raise NotImplementedError(
            "OpenAI provider not configured"
        )