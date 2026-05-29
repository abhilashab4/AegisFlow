from app.services.streaming.stream_validator import (
    StreamValidator
)

from app.services.providers.provider_router import (
    ProviderRouter
)


validator = StreamValidator()

provider_router = ProviderRouter()


async def stream_llm_response(prompt: str):

    accumulated_text = ""

    async for delta in (
        provider_router.stream_generate(
            prompt=prompt
        )
    ):

        if not delta:
            continue

        accumulated_text += delta


        validation = (
            validator.validate_chunk(
                accumulated_text
            )
        )


        if not validation["safe"]:

            yield (
                "\n\n"
                "[STREAM TERMINATED: "
                "POLICY VIOLATION DETECTED]"
            )

            return


        yield delta