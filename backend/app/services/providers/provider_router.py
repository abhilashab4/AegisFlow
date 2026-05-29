from app.services.providers.groq_provider import (
    GroqProvider
)


class ProviderRouter:

    def __init__(self):

        self.providers = {

            "groq": GroqProvider()
        }

        self.default_provider = "groq"


    async def generate(
        self,
        prompt: str,
        provider: str = None
    ):

        provider_name = (
            provider
            or self.default_provider
        )

        selected_provider = (
            self.providers[provider_name]
        )

        return await selected_provider.generate(
            prompt
        )


    async def stream_generate(
        self,
        prompt: str,
        provider: str = None
    ):

        provider_name = (
            provider
            or self.default_provider
        )

        selected_provider = (
            self.providers[provider_name]
        )

        async for chunk in (
            selected_provider.stream_generate(
                prompt
            )
        ):

            yield chunk