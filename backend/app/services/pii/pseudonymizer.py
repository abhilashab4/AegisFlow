"""
Module: Pseudonymizer

Purpose:
Replaces detected Personally Identifiable Information (PII) with unique,
consistent pseudonym tokens while preserving the structure of the original
text. It also maintains an entity mapping that links each original PII value
to its generated token for traceability or future restoration.

Technical Workflow:
1. Initializes an entity map (dictionary) to store mappings between original
   PII values and their corresponding pseudonym tokens.
2. Generates a unique token for each entity using:
   - Entity type (e.g., PERSON, EMAIL, PHONE)
   - A UUID-based unique identifier
   Example: PERSON_TOKEN_A1B2C3D4
3. Sorts all detected entities in descending order of their starting position
   (right-to-left replacement).
4. Replaces each detected PII entity with its corresponding token:
   - If the same PII value has already been encountered, reuses the existing
     token to maintain consistency across the document.
   - Otherwise, generates a new token and stores it in the entity map.
5. Returns:
   - The sanitized text with all detected PII replaced by pseudonym tokens.
   - The entity map containing original PII values and their generated tokens.

Why Right-to-Left Replacement?
Each detected entity stores its original start and end indices. Replacing an
entity at the beginning of the text changes the string length, causing the
indices of subsequent entities to shift. By processing entities from right
to left, the indices of entities that are yet to be replaced remain valid,
eliminating the need to recalculate their positions.

Example:
Original Text:
"John lives in Delhi"

Detected Entities:
- John  (start=0, end=4)
- Delhi (start=14, end=19)

Incorrect (Left-to-Right):
Replace "John" first → "PERSON_TOKEN_A1B2C3D4 lives in Delhi"

The replacement token is longer than "John", causing "Delhi" to shift to a
new position. Its original indices (14–19) are now invalid, leading to
incorrect replacements.

Correct (Right-to-Left):
Replace "Delhi" first → "John lives in LOCATION_TOKEN_X7Y8Z9A1"
Replace "John" next  → "PERSON_TOKEN_A1B2C3D4 lives in LOCATION_TOKEN_X7Y8Z9A1"

Since replacements begin from the end of the text, earlier entity indices
never change, ensuring every replacement occurs at the correct location.

Example Usage:
pseudonymizer = Pseudonymizer()

result = pseudonymizer.pseudonymize(
    "My name is John and my email is john@gmail.com.",
    detections
)

Replacement Flow:
Input Text
    │
    ▼
Detected PII Entities
    │
    ▼
Sort Right-to-Left
    │
    ▼
Generate / Reuse Token
    │
    ▼
Replace PII with Token
    │
    ▼
Update Entity Map
    │
    ▼
Return Sanitized Text + Entity Map

Benefits:
- Generates unique pseudonym tokens using UUIDs.
- Ensures the same PII value always maps to the same token throughout the text.
- Preserves correct replacement indices using right-to-left processing.
- Maintains an entity map for traceability and potential de-pseudonymization.
- Protects sensitive information while preserving the readability and
  structure of the original document.
"""



import uuid


class Pseudonymizer:

    def __init__(self):
        self.entity_map = {}

    def _generate_token(self, entity_type: str):
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{entity_type}_TOKEN_{unique_id}"

    def pseudonymize(self, text: str, detections: list):
        detections = sorted(
            detections, key=lambda x: x["start"], reverse=True
        )

        modified_text = text

        for d in detections:
            start = d.get("start")
            end = d.get("end")
            original = d.get("match", "")
            entity_type = d.get("entity_type", "PII")

            if start is None or end is None or start >= end:
                continue

            lookup_key = original.strip().lower()

            if lookup_key in self.entity_map:
                token = self.entity_map[lookup_key]
            else:
                token = self._generate_token(entity_type)
                self.entity_map[lookup_key] = token

            modified_text = (
                modified_text[:start] + token + modified_text[end:]
            )

        return {
            "sanitized_text": modified_text,
            "entity_map": {k: v for k, v in self.entity_map.items()},
        }