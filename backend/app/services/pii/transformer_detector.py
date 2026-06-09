from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

class TransformerDetector:

    def __init__(self):
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }

        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        nlp_engine = provider.create_engine()

        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

        self.entities = [
            "PERSON",
            "LOCATION",
            "ORGANIZATION",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
        ]

    def detect(self, text: str):
        results = self.analyzer.analyze(
            text=text,
            language="en",
            entities=self.entities,
            score_threshold=0.6
        )

        detections = []
        for r in results:
            detections.append({
                "entity_type": r.entity_type,
                "match": text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "confidence": r.score,
                "detector": "transformer"
            })

        return detections