from app.services.pii.regex_detector import RegexDetector
from app.services.pii.transformer_detector import TransformerDetector
from app.services.pii.pseudonymizer import Pseudonymizer
from app.services.pii.verifier import VerificationEngine


class PIIPipeline:

    def __init__(self):

        self.regex_detector = RegexDetector()

        self.transformer_detector = TransformerDetector()

        self.pseudonymizer = Pseudonymizer()

        self.verifier = VerificationEngine()


    def sanitize_prompt(self, text: str):

        regex_results = self.regex_detector.detect(text)

        transformer_results = (
            self.transformer_detector.detect(text)
        )

        all_detections = (
            regex_results +
            transformer_results
        )

        unique_detections = []

        seen = set()

        for d in all_detections:

            key = (
                d["start"],
                d["end"],
                d["entity_type"]
            )

            if key not in seen:
                seen.add(key)
                unique_detections.append(d)

        pseudonymized = (
            self.pseudonymizer.pseudonymize(
                text,
                unique_detections
            )
        )

        sanitized_text = (
            pseudonymized["sanitized_text"]
        )

        verification = (
            self.verifier.verify(sanitized_text)
        )

        if not verification["safe"]:

            return {
                "safe": False,
                "reason": "Residual PII detected",
                "residual_pii": verification[
                    "residual_pii"
                ]
            }

        return {
            "safe": True,
            "original_text": text,
            "sanitized_text": sanitized_text,
            "entity_map": pseudonymized[
                "entity_map"
            ],
            "detections": unique_detections
        }