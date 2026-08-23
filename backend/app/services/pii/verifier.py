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