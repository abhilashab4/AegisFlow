from app.services.pii.regex_detector import RegexDetector
from app.services.pii.transformer_detector import TransformerDetector


class VerificationEngine:

    def __init__(self):

        self.regex_detector = RegexDetector()
        self.transformer_detector = TransformerDetector()

    def verify(self, text: str):

        regex_results = self.regex_detector.detect(text)

        transformer_results = self.transformer_detector.detect(text)

        residual_pii = (
            regex_results +
            transformer_results
        )

        filtered_results = []

        for r in residual_pii:

            value = r["match"]

            if "_TOKEN_" not in value:
                filtered_results.append(r)

        if filtered_results:

            return {
                "safe": False,
                "residual_pii": filtered_results
            }

        return {
            "safe": True,
            "residual_pii": []
        }