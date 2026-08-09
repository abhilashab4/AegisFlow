class OutputGuardrail:

    def __init__(self, policy_service):

        self.policy_service = policy_service

    async def validate(self, text: str):

        policy = await self.policy_service.find_matching_policy(
            text
        )

        # No matching policy
        if not policy:

            return {
                "safe": True,
                "action": "ALLOW",
                "risk_score": 0.0
            }

        similarity = policy["similarity"]

        threshold = policy["threshold"]

        # Policy violation
        if similarity >= threshold:

            return {
                "safe": False,
                "action": policy["action"],
                "category": policy["category"],
                "risk_score": round(
                    similarity,
                    4
                ),
                "reason": policy["description"],
                "replacement": (
                    "This response was blocked because "
                    "it may violate corporate compliance policies."
                )
            }

        return {
            "safe": True,
            "action": "ALLOW",
            "risk_score": round(
                similarity,
                4
            )
        }