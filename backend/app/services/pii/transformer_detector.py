import re

class OutputGuardrail:

    def __init__(self):

        self.patterns = {
            "violence_weapons": [
                r"\bbomb\b",
                r"\bexplosive(s)?\b",
                r"\bweapon(s)?\b",
                r"\bgun(s)?\b",
                r"\bgrenade(s)?\b"
            ],

            "cybercrime": [
                r"\bhack(ing)?\b",
                r"\bcrack(ing)?\b",
                r"\bmalware\b",
                r"\bvirus\b",
                r"\btrojan\b",
                r"\bphishing\b",
                r"\bsql\s*injection\b"
            ],

            "fraud_theft": [
                r"\bfraud\b",
                r"\bscam\b",
                r"\bcredit\s*card\s*theft\b",
                r"\bidentity\s*theft\b",
                r"\bstolen\b"
            ],

            "drugs_illegal": [
                r"\bcocaine\b",
                r"\bheroin\b",
                r"\bmeth\b",
                r"\bmdma\b",
                r"\billegal\s*drug(s)?\b"
            ]
        }

        self.obfuscation_patterns = [
            r"h[\W_]*a[\W_]*c[\W_]*k",
            r"b[\W_]*o[\W_]*m[\W_]*b",
            r"w[\W_]*e[\W_]*a[\W_]*p[\W_]*o[\W_]*n",
            r"f[\W_]*r[\W_]*a[\W_]*u[\W_]*d"
        ]

    def normalize(self, text: str):
        return text.lower()

    def check_obfuscation(self, text: str):

        for pattern in self.obfuscation_patterns:
            if re.search(pattern, text):
                return {
                    "safe": False,
                    "reason": "Obfuscated harmful content detected",
                    "layer": "obfuscation"
                }

        return {"safe": True}

    def check_patterns(self, text: str):

        hits = []

        for category, patterns in self.patterns.items():

            for pattern in patterns:
                if re.search(pattern, text):
                    hits.append(category)
                    break

        if hits:
            return {
                "safe": False,
                "reason": f"Harmful categories detected: {', '.join(hits)}",
                "layer": "regex",
                "categories": hits
            }

        return {"safe": True}

    def validate_llm_output(self, llm_response: str):

        text = self.normalize(llm_response)

        obf = self.check_obfuscation(text)
        if not obf["safe"]:
            return obf

        result = self.check_patterns(text)
        if not result["safe"]:
            return result

        return {
            "safe": True,
            "layer": "clean"
        }