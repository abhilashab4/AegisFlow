"""
Module: PII Sanitization Pipeline

Purpose:
Implements an end-to-end Personally Identifiable Information (PII) sanitization
pipeline. It detects sensitive information using both rule-based (Regex) and
Transformer-based models, removes duplicate/overlapping detections, replaces
PII with pseudonyms, verifies that no sensitive information remains, and
returns a sanitized prompt that is safe for downstream processing.

Technical Workflow:
1. Initializes the core pipeline components:
   - RegexDetector for pattern-based PII detection.
   - TransformerDetector for ML-based Named Entity Recognition (NER).
   - Pseudonymizer for replacing detected PII with placeholders.
   - VerificationEngine for validating the sanitized output.
2. Detects PII using both Regex and Transformer models.
3. Merges all detections and ranks them by:
   - Higher confidence score.
   - Longer entity span (to resolve overlapping entities).
4. Removes duplicate or overlapping detections. If both detectors identify
   the same or intersecting text (e.g., "john@gmail.com" as an EMAIL and
   "john" as a PERSON), the pipeline keeps only the highest-priority
   detection based on confidence and entity length. This prevents multiple
   replacements of the same text during pseudonymization.
5. Sorts the remaining detections by their starting position in the original
   text so that entities are replaced from left to right, preserving correct
   text alignment during pseudonymization.
6. Replaces detected entities with pseudonyms while maintaining an entity map.
7. Verifies the sanitized text to ensure no residual PII remains.
8. Returns either:
   - A successful sanitization result containing the sanitized text,
     entity mapping, and detected entities, or
   - A failure response if residual PII is still detected.

Example Usage:
pipeline = PIIPipeline()

result = pipeline.sanitize_prompt(
    "My name is John Doe and my email is john@gmail.com."
)

Pipeline Flow:
Input Text
    │
    ▼
Regex Detector + Transformer Detector
    │
    ▼
Merge & Rank Detections
    │
    ▼
Remove Overlapping Entities
    │
    ▼
Pseudonymize PII
    │
    ▼
Verify Sanitized Text
    │
    ├── Residual PII Found ──► Return Unsafe Response
    │
    └── No Residual PII
            │
            ▼
      Return Sanitized Output

Benefits:
- Combines rule-based and AI-based PII detection for higher accuracy.
- Resolves overlapping detections using confidence and entity span.
- Preserves document structure through pseudonymization.
- Ensures sanitized output is safe using a secondary verification step.
- Produces an entity mapping for traceability and potential de-pseudonymization.
"""




from app.services.pii.pseudonymizer import Pseudonymizer
from app.services.pii.regex_detector import RegexDetector
from app.services.pii.transformer_detector import TransformerDetector
from app.services.pii.verifier import VerificationEngine


class PIIPipeline:

    def __init__(self):
        self.regex_detector = RegexDetector()
        self.transformer_detector = TransformerDetector()
        self.pseudonymizer = Pseudonymizer()
        self.verifier = VerificationEngine()

    def sanitize_prompt(self, text: str):
        regex_results = self.regex_detector.detect(text)
        transformer_results = self.transformer_detector.detect(text)

        all_detections = regex_results + transformer_results

        all_detections = sorted(
            all_detections,
            key=lambda x: (
                -x.get("confidence", 0),
                -(x["end"] - x["start"]),
            ),
        )

        unique_detections = []
        occupied = set()

        for d in all_detections:
            span = set(range(d["start"], d["end"]))

            if occupied.intersection(span):
                continue

            unique_detections.append(d)
            occupied.update(span)

        unique_detections.sort(key=lambda x: x["start"])

        pseudonymized = self.pseudonymizer.pseudonymize(
            text, unique_detections
        )

        sanitized_text = pseudonymized["sanitized_text"]

        verification = self.verifier.verify(sanitized_text)

        if not verification["safe"]:
            return {
                "safe": False,
                "reason": "Residual PII detected",
                "sanitized_text": sanitized_text,
                "residual_pii": verification["residual_pii"],
            }

        return {
            "safe": True,
            "original_text": text,
            "sanitized_text": sanitized_text,
            "entity_map": pseudonymized["entity_map"],
            "detections": unique_detections,
        }