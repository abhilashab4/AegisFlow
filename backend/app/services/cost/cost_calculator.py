MODEL_PRICING = {

    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08
    },

    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },

    "claude-3-5-sonnet": {
        "input": 3.00,
        "output": 15.00
    }
}


def estimate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
):

    pricing = MODEL_PRICING.get(model)

    if not pricing:
        return 0.0

    input_cost = (
        prompt_tokens / 1_000_000
    ) * pricing["input"]

    output_cost = (
        completion_tokens / 1_000_000
    ) * pricing["output"]

    return round(
        input_cost + output_cost,
        6
    )