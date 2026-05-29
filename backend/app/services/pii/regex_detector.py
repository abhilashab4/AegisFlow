import re


class RegexDetector:

    def __init__(self):

        self.patterns = {

            "PHONE_NUMBER": re.compile(
                r"\b\d{10}\b"
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
        }


    def detect(self, text: str):

        detections = []

        for entity_type, pattern in self.patterns.items():

            matches = pattern.finditer(text)

            for match in matches:

                detections.append({
                    "entity_type": entity_type,
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0,
                    "detector": "regex"
                })

        return detections