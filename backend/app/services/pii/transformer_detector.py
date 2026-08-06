"""
Module: Transformer Detector

Purpose:
Implements an AI-based PII detection engine using Microsoft Presidio Analyzer
with a spaCy NLP model. Unlike Regex-based detection, this module identifies
context-based PII entities such as names, locations, and organizations by
understanding the meaning and context of the text. It enhances the overall PII
pipeline by detecting entities that do not follow fixed patterns.

Technical Workflow:
1. Initializes the NLP engine:
   - Uses spaCy as the NLP backend.
   - Loads the en_core_web_sm language model for English text processing.
   - Creates a Presidio AnalyzerEngine for Named Entity Recognition (NER).

2. Defines supported PII entity types:
   - PERSON
   - LOCATION
   - ORGANIZATION
   - EMAIL_ADDRESS
   - PHONE_NUMBER
   - URL
   - IP_ADDRESS

3. Analyzes input text using Presidio:
   - Runs NLP-based entity recognition.
   - Uses a confidence threshold (0.45) to filter low-confidence detections.
   - Extracts detected entities with their text positions and confidence scores.

4. Removes duplicate detections:
   - Maintains a set of already detected entities using:
     (start position, end position, entity type)
   - Prevents duplicate entity entries from being returned.

5. Improves confidence using contextual information:
   - Examines a 50-character window around each detected entity.
   - Checks for related keywords that indicate stronger PII context.
   
   Example:
   Input:
   "Contact John for the project"

   Initial detection:
   PERSON: John (confidence = 0.80)

   Context keyword:
   "contact"

   Updated confidence:
   PERSON: John (confidence = 0.95)

6. Creates detection metadata containing:
   - Entity type
   - Detected text value
   - Start and end character positions
   - Confidence score
   - Detection source ("transformer")

7. Sorts detections by their original text position and returns the final
   list of transformer-based PII detections.

Example Usage:
detector = TransformerDetector()

detections = detector.detect(
    "John works at Google and can be contacted through email."
)

Example Output:
[
    {
        "entity_type": "PERSON",
        "match": "John",
        "start": 0,
        "end": 4,
        "confidence": 0.95,
        "detector": "transformer"
    },
    {
        "entity_type": "ORGANIZATION",
        "match": "Google",
        "start": 15,
        "end": 21,
        "confidence": 0.88,
        "detector": "transformer"
    }
]

Detection Flow:
Input Text
    │
    ▼
spaCy NLP Model
    │
    ▼
Presidio AnalyzerEngine
    │
    ▼
Named Entity Recognition (NER)
    │
    ▼
Confidence Filtering
    │
    ▼
Context-Based Confidence Boosting
    │
    ▼
Remove Duplicate Detections
    │
    ▼
Return PII Entities

Why Transformer-Based Detection?
Regex works well for structured PII such as emails and phone numbers, but it
cannot understand context. Transformer/NLP-based detection identifies
unstructured PII such as names, locations, and organizations by analyzing the
meaning of surrounding words.

Example:
"Apple released a new product."
"Contact Apple at support."

Regex cannot determine whether "Apple" is a company or a fruit, but an NLP
model can use surrounding context to classify the entity correctly.

Benefits:
- Detects context-based PII that Regex cannot identify.
- Provides confidence scores for intelligent filtering.
- Uses contextual boosting to improve detection reliability.
- Complements Regex detection for better overall PII coverage.
- Provides exact entity positions for accurate pseudonymization.
"""


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