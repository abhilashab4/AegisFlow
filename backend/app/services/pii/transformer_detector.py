from presidio_analyzer import AnalyzerEngine


class TransformerDetector:

    def __init__(self):

        self.analyzer = AnalyzerEngine()

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