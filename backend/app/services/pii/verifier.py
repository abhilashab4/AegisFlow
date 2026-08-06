"""
Module: Verification Engine

Purpose:
Implements a final validation layer for the PII sanitization pipeline. It
checks the generated sanitized text again using both Regex-based and
Transformer-based detectors to ensure that no sensitive information remains
after pseudonymization. This acts as a safety layer before allowing the text
to be processed further.

Technical Workflow:
1. Initializes detection components:
   - RegexDetector for structured PII detection.
   - TransformerDetector for context-based PII detection.

2. Re-scans the sanitized text:
   - Runs both detectors on the pseudonymized output.
   - Combines all detected entities into a single residual PII list.

3. Removes duplicate detections:
   - Uses entity position (start and end indices) as a unique identifier.
   - If multiple detectors identify the same entity, keeps the detection with
     the highest confidence score.

4. Filters false residual detections:
   - Ignores already pseudonymized tokens such as:
     PERSON_TOKEN_xxxxx, EMAIL_ADDRESS_TOKEN_xxxxx, etc.
   - Removes weak Transformer-based detections with confidence below 0.70 to
     avoid false positives from low-confidence NER results.

5. Returns verification status:
   - If remaining PII is detected:
        safe = False
        Returns the residual PII details.
   - If no PII remains:
        safe = True
        Returns an empty residual PII list.

Example Usage:
verifier = VerificationEngine()

result = verifier.verify(
    "My email is EMAIL_ADDRESS_TOKEN_A1B2C3D4"
)

Example Output:
{
    "safe": True,
    "residual_pii": []
}

Unsafe Example:
Input:
"My email is EMAIL_ADDRESS_TOKEN_A1B2C3D4 and phone is 9876543210"

Output:
{
    "safe": False,
    "residual_pii": [
        {
            "entity_type": "PHONE_NUMBER",
            "match": "9876543210",
            "confidence": 1.0
        }
    ]
}

Verification Flow:

Sanitized Text
      │
      ▼
Regex Detection + Transformer Detection
      │
      ▼
Combine Residual Detections
      │
      ▼
Remove Duplicate Entities
      │
      ▼
Ignore Existing Pseudonym Tokens
      │
      ▼
Filter Low Confidence Results
      │
      ▼
Residual PII Found?
      │
      ├── Yes → Return Unsafe Response
      │
      └── No  → Return Safe Response

Why Verification is Required?
Although pseudonymization replaces detected PII, a second verification step is
needed because detection models may miss entities during the first pass.
Running detection again on the sanitized output provides an additional safety
check and prevents accidental leakage of sensitive information.

Benefits:
- Provides an additional security layer after pseudonymization.
- Detects missed PII before data leaves the system.
- Combines rule-based and AI-based verification for better coverage.
- Reduces false positives using token filtering and confidence thresholds.
- Ensures sanitized prompts are safe for downstream processing.
"""


from app.services.pii.regex_detector import RegexDetector
from app.services.pii.transformer_detector import TransformerDetector


class VerificationEngine:

    def __init__(self):
        self.regex_detector = RegexDetector()
        self.transformer_detector = TransformerDetector()

    def verify(self, text: str):
        regex_results = self.regex_detector.detect(text)
        transformer_results = self.transformer_detector.detect(text)

        residual_pii = regex_results + transformer_results

        unique = {}

        for r in residual_pii:
            key = (r["start"], r["end"])

            if (
                key not in unique
                or r["confidence"] > unique[key]["confidence"]
            ):
                unique[key] = r

        residual_pii = list(unique.values())

        filtered_results = []

        token_prefixes = (
            "PERSON_TOKEN_",
            "LOCATION_TOKEN_",
            "ORGANIZATION_TOKEN_",
            "EMAIL_ADDRESS_TOKEN_",
            "PHONE_NUMBER_TOKEN_",
            "IP_ADDRESS_TOKEN_",
            "URL_TOKEN_",
            "AADHAAR_TOKEN_",
            "PAN_NUMBER_TOKEN_",
            "GSTIN_TOKEN_",
            "IFSC_CODE_TOKEN_",
            "PASSPORT_TOKEN_",
            "UPI_ID_TOKEN_",
            "CREDIT_CARD_TOKEN_",
            "US_SSN_TOKEN_",
        )

        for r in residual_pii:
            value = r["match"]

            # Ignore already pseudonymized values
            if value.startswith(token_prefixes):
                continue

            # Ignore weak NER hits
            if (
                r["detector"] == "transformer"
                and r["confidence"] < 0.70
            ):
                continue

            filtered_results.append(r)

        if filtered_results:
            return {
                "safe": False,
                "residual_pii": sorted(
                    filtered_results, key=lambda x: x["start"]
                ),
            }

        return {"safe": True, "residual_pii": []}