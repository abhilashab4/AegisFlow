from sentence_transformers import CrossEncoder
import numpy as np

class OutputGuardrail:

    def __init__(self):

        self.blocked_keywords = [
            "bomb",
            "explosive",
            "malware",
            "hack",
            "credit card theft",
            "fraud",
            "illegal activity",
            "weapon",
        ]


        self.semantic_model = CrossEncoder(
            "cross-encoder/nli-distilroberta-base"
        )

        self.policy_statement = (
            "This response promotes harmful, "
            "illegal, or unsafe activity."
        )

    def keyword_check(self, text: str):

        lowered = text.lower()

        for word in self.blocked_keywords:

            if word in lowered:

                return {
                    "safe": False,
                    "reason": (
                        f"Blocked keyword detected: "
                        f"{word}"
                    ),
                    "layer": "keyword"
                }

        return {"safe": True}


    def semantic_check(self, text: str):

        scores = self.semantic_model.predict([
            (
                text,
                self.policy_statement
            )
        ])

        print("DEBUG: Raw semantic scores =", scores)


        entailment_score = float(scores[0][2])

        print(
            "DEBUG: Entailment score =",
            entailment_score
        )

        if entailment_score > 5.0:

            return {
                "safe": False,
                "reason": (
                    "Semantic policy "
                    "violation detected"
                ),
                "layer": "semantic",
                "score": entailment_score
            }

        return {
            "safe": True,
            "score": entailment_score
        }

    def validate(self, text: str):

        keyword_result = (
            self.keyword_check(text)
        )

        if not keyword_result["safe"]:
            return keyword_result

        semantic_result = (
            self.semantic_check(text)
        )

        if not semantic_result["safe"]:
            return semantic_result

        return {
            "safe": True
        }