import uuid


class Pseudonymizer:

    def __init__(self):

        self.entity_map = {}


    def _generate_token(self, entity_type: str):

        unique_id = str(uuid.uuid4())[:6].upper()

        return f"{entity_type}_TOKEN_{unique_id}"


    def pseudonymize(self, text: str, detections: list):

        detections = sorted(
            detections,
            key=lambda x: x["start"],
            reverse=True
        )

        modified_text = text

        for d in detections:

            original = d["match"]
            entity_type = d["entity_type"]

            if original in self.entity_map:
                token = self.entity_map[original]
            else:
                token = self._generate_token(entity_type)
                self.entity_map[original] = token

            modified_text = (
                modified_text[:d["start"]]
                + token
                + modified_text[d["end"]:]
            )

        return {
            "sanitized_text": modified_text,
            "entity_map": self.entity_map
        }