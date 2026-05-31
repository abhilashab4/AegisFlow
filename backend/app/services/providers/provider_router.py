from app.services.providers.groq_provider import (
    GroqProvider
)

# Future imports
# from app.services.providers.openai_provider import (
#     OpenAIProvider
# )
#
# from app.services.providers.claude_provider import (
#     ClaudeProvider
# )


class ProviderRouter:

    def __init__(self):


        self.providers = {

            "groq":
                GroqProvider(),

            # "openai":
            #     OpenAIProvider(),

            # "anthropic":
            #     ClaudeProvider(),
        }


        self.model_provider_mapping = {

            # Groq Models
            "llama-3.1-8b-instant":
                "groq",

            "llama-3.3-70b-versatile":
                "groq",

            "qwen-2.5-coder":
                "groq",

            # Future OpenAI Models
            "gpt-4o-mini":
                "openai",

            "gpt-4.1":
                "openai",

            # Future Anthropic Models
            "claude-3-5-sonnet":
                "anthropic"
        }


    def resolve_provider(
        self,
        model: str
    ):

        provider = (
            self.model_provider_mapping.get(
                model
            )
        )

        if not provider:

            raise ValueError(
                f"No provider mapped for model: {model}"
            )

        if provider not in self.providers:

            raise ValueError(
                f"Provider '{provider}' "
                f"not registered"
            )

        return provider


    async def generate(
        self,
        prompt: str,
        model: str
    ):

        provider_name = (
            self.resolve_provider(model)
        )

        selected_provider = (
            self.providers[provider_name]
        )

        return await (
            selected_provider.generate(
                prompt=prompt,
                model=model
            )
        )

    async def stream_generate(
        self,
        prompt: str,
        model: str
    ):

        provider_name = self.resolve_provider(
            model
        )

        selected_provider = (
            self.providers[provider_name]
        )

        async for chunk in (
            selected_provider.stream_generate(
                prompt=prompt,
                model=model
            )
        ):
            yield chunk