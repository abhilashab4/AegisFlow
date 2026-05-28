import logging

logger = logging.getLogger(__name__)

async def check_output_guardrails(text: str) -> dict:


    policy_map = {
        "hack": "Cybersecurity Risk",
        "create malware": "Cybersecurity Risk",
        "steal credit card": "Financial Fraud",
        "commit fraud": "Financial Fraud",
        "illegal activity": "Legal/Compliance"
    }

    try:
        lowered_text = text.lower()
        
        for phrase, category in policy_map.items():
            if phrase in lowered_text:
                logger.warning(f"Guardrail triggered. Category: {category}, Phrase: '{phrase}'")
                return {
                    "safe": False, 
                    "category": category,
                    "reason": f"Content policy violation: '{phrase}' detected."
                }
        
        return {"safe": True, "reason": None}

    except Exception as e:
        logger.error(f"Guardrail processing error: {str(e)}")
        return {"safe": False, "reason": "Internal guardrail error."}