from app.services.providers.base_provider import (
    BaseLLMProvider
)


class ClaudeProvider(
    BaseLLMProvider
):

    async def generate(
        self,
        prompt: str,
        model: str
    ):

        raise NotImplementedError(
            "Claude provider not configured"
        )

    async def stream_generate(
        self,
        prompt: str,
        model: str
    ):

        raise NotImplementedError(
            "Claude provider not configured"
        )