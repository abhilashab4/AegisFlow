import re

class OutputGuardrail:

    def __init__(self):

        # Strong regex patterns (normalized + obfuscated + variations)
        self.patterns = {
            "malware": [
                r"\bmalware\b",
                r"\bvirus\b",
                r"\btrojan\b",
                r"\bspyware\b",
                r"\bransomware\b"
            ],

            "hacking": [
                r"\bhack(ing)?\b",
                r"\bcrack(ing)?\b",
                r"\bunauthori[sz]ed access\b",
                r"\bexploit\b",
                r"\bbreach\b",
                r"\bsql\s*injection\b"
            ],

            "weapons": [
                r"\bbomb\b",
                r"\bexplosive(s)?\b",
                r"\bweapon(s)?\b",
                r"\bfirearm(s)?\b",
                r"\bgun\b",
                r"\bgrenade\b"
            ],

            "fraud": [
                r"\bfraud\b",
                r"\bscam\b",
                r"\bphish(ing)?\b",
                r"\bstolen\s*credit\s*card\b",
                r"\bcredit\s*card\s*theft\b",
                r"\bidentity\s*theft\b"
            ],

            "drug_illegal": [
                r"\bcocaine\b",
                r"\bheroin\b",
                r"\bmdma\b",
                r"\bmeth\b",
                r"\billegal\s*drug(s)?\b"
            ]
        }

        # Obfuscation handling (b@ck, h4ck, b0mb etc.)
        self.obfuscation_patterns = [
            r"h[\W_]*a[\W_]*c[\W_]*k",
            r"b[\W_]*o[\W_]*m[\W_]*b",
            r"w[\W_]*e[\W_]*a[\W_]*p[\W_]*o[\W_]*n",
            r"f[\W_]*r[\W_]*a[\W_]*u[\W_]*d"
        ]

    # -----------------------------
    # Step 1: Obfuscation detection
    # -----------------------------
    def obfuscation_check(self, text: str):

        lowered = text.lower()

        for pattern in self.obfuscation_patterns:
            if re.search(pattern, lowered):
                return {
                    "safe": False,
                    "reason": f"Obfuscated harmful intent detected: {pattern}",
                    "layer": "obfuscation"
                }

        return {"safe": True}

    # -----------------------------
    # Step 2: Regex classification
    # -----------------------------
    def keyword_check(self, text: str):

        lowered = text.lower()
        reasons = []

        for category, patterns in self.patterns.items():

            for pattern in patterns:

                if re.search(pattern, lowered):
                    reasons.append(category)
                    break

        if reasons:
            return {
                "safe": False,
                "reason": f"Blocked categories detected: {', '.join(reasons)}",
                "layer": "regex",
                "categories": reasons
            }

        return {"safe": True}

    # -----------------------------
    # Main validator
    # -----------------------------
    def validate(self, text: str):

        # 1. Obfuscation layer (highest priority)
        obf = self.obfuscation_check(text)
        if not obf["safe"]:
            return obf

        # 2. Regex classification layer
        result = self.keyword_check(text)
        if not result["safe"]:
            return result

        return {
            "safe": True,
            "layer": "clean"
        }