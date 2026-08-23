from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider


class TransformerDetector:

    def __init__(self):
        self.analyzer = None

        self.entities = [
            "PERSON",
            "LOCATION",
            "ORGANIZATION",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "URL",
            "IP_ADDRESS",
        ]

        self.context_words = {
            "PERSON": [
                "name",
                "called",
                "contact",
                "employee",
                "customer",
            ],
            "EMAIL_ADDRESS": [
                "email",
                "mail",
                "gmail",
                "outlook",
            ],
            "PHONE_NUMBER": [
                "phone",
                "mobile",
                "call",
                "contact",
            ],
            "ORGANIZATION": [
                "company",
                "organization",
                "firm",
                "startup",
            ],
        }

    def _get_analyzer(self):
        if self.analyzer is None:
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {
                        "lang_code": "en",
                        "model_name": "en_core_web_sm",
                    }
                ],
            }

            provider = NlpEngineProvider(
                nlp_configuration=nlp_configuration
            )

            nlp_engine = provider.create_engine()

            self.analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine,
                supported_languages=["en"],
            )

        return self.analyzer

    def _boost_confidence(self, text, detection):
        start = detection["start"]
        end = detection["end"]

        window_start = max(0, start - 50)
        window_end = min(len(text), end + 50)

        context = text[window_start:window_end].lower()

        for word in self.context_words.get(
            detection["entity_type"], []
        ):
            if word in context:
                detection["confidence"] = min(
                    detection["confidence"] + 0.15,
                    1.0,
                )

        return detection

    def detect(self, text: str):
        analyzer = self._get_analyzer()

        results = analyzer.analyze(
            text=text,
            language="en",
            entities=self.entities,
            score_threshold=0.45,
        )

        detections = []
        seen = set()

        for r in results:
            key = (
                r.start,
                r.end,
                r.entity_type,
            )

            if key in seen:
                continue

            seen.add(key)

            detection = {
                "entity_type": r.entity_type,
                "match": text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "confidence": round(float(r.score), 4),
                "detector": "transformer",
            }

            detection = self._boost_confidence(
                text,
                detection,
            )

            detections.append(detection)

        detections.sort(
            key=lambda x: (
                x["start"],
                -x["confidence"],
            )
        )

        return detections