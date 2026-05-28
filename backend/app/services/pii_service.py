import asyncio
from concurrent.futures import ThreadPoolExecutor
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
executor = ThreadPoolExecutor()

async def sanitize_text(text: str):
    """
    Sanitizes PII in text asynchronously. 
    Uses a ThreadPoolExecutor to prevent blocking the event loop 
    during heavy NLP analysis.
    """
    loop = asyncio.get_event_loop()
    
    results = await loop.run_in_executor(
        executor, 
        lambda: analyzer.analyze(
            text=text, 
            language="en", 
            score_threshold=0.6,
            entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN", "IBAN_CODE", "IP_ADDRESS"]
        )
    )

    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE_NUMBER>"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_ADDRESS>"}),
        "CREDIT_CARD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 12, "from_end": True}),
        "US_SSN": OperatorConfig("replace", {"new_value": "<SSN>"}),
        "IBAN_CODE": OperatorConfig("replace", {"new_value": "<IBAN>"}),
        "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP_ADDRESS>"}),
    }

    anonymized = await loop.run_in_executor(
        executor,
        lambda: anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
    )

    return {
        "sanitized_text": anonymized.text,
        "pii_detected": len(results) > 0
    }