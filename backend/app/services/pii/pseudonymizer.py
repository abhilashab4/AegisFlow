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