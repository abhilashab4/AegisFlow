from app.services.providers.provider_router import (
    ProviderRouter
)

from app.services.streaming.stream_validator import (
    StreamValidator
)

provider_router = ProviderRouter()

validator = StreamValidator()


async def stream_llm_response(
    prompt: str,
    model: str = None
):

    buffer = ""

    async for chunk in provider_router.stream_generate(
        prompt=prompt,
        model=model
    ):

        if not chunk:
            continue

        buffer += chunk

        if len(buffer) >= 256:

            validation = validator.validate_chunk(
                buffer
            )

            if not validation["safe"]:

                yield (
                    "\n\n"
                    "[STREAM TERMINATED: "
                    "POLICY VIOLATION]"
                )

                return

            buffer = ""

        yield chunk

    if buffer:

        validation = validator.validate_chunk(
            buffer
        )

        if not validation["safe"]:

            yield (
                "\n\n"
                "[STREAM TERMINATED: "
                "POLICY VIOLATION]"
            )

            return