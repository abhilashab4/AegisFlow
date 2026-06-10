import re


class RegexDetector:

    def __init__(self):

        self.patterns = {

            # India + generic international numbers
            "PHONE_NUMBER": re.compile(
                r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"
            ),

            "EMAIL_ADDRESS": re.compile(
                r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
            ),

            "CREDIT_CARD": re.compile(
                r"\b(?:\d[ -]*?){13,16}\b"
            ),

            "IP_ADDRESS": re.compile(
                r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
            ),

            "US_SSN": re.compile(
                r"\b\d{3}-\d{2}-\d{4}\b"
            ),

            "AADHAAR": re.compile(
                r"\b\d{4}\s?\d{4}\s?\d{4}\b"
            ),

            "PAN_NUMBER": re.compile(
                r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
            ),

            "PASSPORT": re.compile(
                r"\b[A-Z][0-9]{7}\b"
            ),

            "GSTIN": re.compile(
                r"\b\d{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b"
            ),

            "IFSC_CODE": re.compile(
                r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
            ),

            "UPI_ID": re.compile(
                r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
            ),

            "URL": re.compile(
                r"(?:https?://|www\.)[^\s]+",
                re.IGNORECASE
            ),
        }

    def _is_valid_credit_card(
        self,
        card_number: str
    ):

        digits = "".join(
            c for c in card_number
            if c.isdigit()
        )

        if not (
            13 <= len(digits) <= 16
        ):
            return False

        total = 0
        reverse_digits = digits[::-1]

        for i, digit in enumerate(
            reverse_digits
        ):

            n = int(digit)

            if i % 2 == 1:

                n *= 2

                if n > 9:
                    n -= 9

            total += n

        return total % 10 == 0

    def detect(
        self,
        text: str
    ):

        detections = []

        for (
            entity_type,
            pattern
        ) in self.patterns.items():

            for match in pattern.finditer(
                text
            ):

                value = match.group()

                # Reduce credit card false positives
                if (
                    entity_type
                    == "CREDIT_CARD"
                ):
                    if not self._is_valid_credit_card(
                        value
                    ):
                        continue

                detections.append({
                    "entity_type": entity_type,
                    "match": value,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0,
                    "detector": "regex"
                })

        return detections