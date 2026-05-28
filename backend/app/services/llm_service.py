import logging
from groq import AsyncGroq, APIError
from app.core.config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)
logger = logging.getLogger(__name__)

async def generate_llm_response(prompt: str) -> str:
    """
    Communicates with the Groq LLM API. 
    Includes error handling for API outages and request timeouts.
    """
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful, secure, and professional enterprise AI assistant. "
                               "Ensure all responses adhere to company compliance policies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            timeout=10.0
        )
        return response.choices[0].message.content

    except APIError as e:
        logger.error(f"Groq API Error: {str(e)}")
        raise Exception("LLM Provider currently unavailable.")
    except Exception as e:
        logger.error(f"Unexpected LLM service error: {str(e)}")
        raise Exception("Failed to generate response from AI agent.")