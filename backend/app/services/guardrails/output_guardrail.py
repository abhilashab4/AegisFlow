"""
Module: Output Guardrail

Purpose:
Implements a policy-based safety layer that validates AI-generated responses
before they are returned to the user. It uses semantic policy matching to
determine whether the output potentially violates corporate compliance or
security policies and either allows or blocks the response.

Technical Workflow:
1. Receives the generated AI response as input.
2. Uses the injected PolicyService to find the most semantically similar
   corporate policy for the response.
3. If no matching policy is found:
   - Marks the response as safe.
   - Sets the action to ALLOW.
   - Returns a risk score of 0.0.
4. If a matching policy is found, retrieves:
   - similarity: semantic similarity between the response and policy.
   - threshold: minimum similarity required to consider it a violation.
   - action: policy-defined action such as BLOCK or WARN.
   - category: type of policy violation.
   - description: explanation of the policy.
5. Compares the similarity score against the policy threshold.
6. If similarity >= threshold:
   - Marks the response as unsafe.
   - Applies the policy-defined action.
   - Returns the policy category, risk score, reason, and a safe replacement
     message instead of allowing the original response.
7. If similarity is below the threshold:
   - The response is considered safe.
   - The response is allowed with its similarity score recorded as the risk score.

Example Usage:
guardrail = OutputGuardrail(policy_service)

result = await guardrail.validate(
    "Here are instructions for bypassing the company's security controls."
)

Example Policy Match:
Generated Response
        │
        ▼
PolicyService.find_matching_policy()
        │
        ▼
Semantic Similarity = 0.91
Policy Threshold   = 0.85
        │
        ▼
0.91 >= 0.85 ?
        │
        ├── Yes → BLOCK
        │          │
        │          ▼
        │     Return safe=False
        │
        └── No  → ALLOW

Decision Flow:
AI Output
   │
   ▼
Find Matching Policy
   │
   ├── No Policy ──────────► ALLOW
   │
   ▼
Calculate / Retrieve Similarity
   │
   ▼
Compare Similarity with Threshold
   │
   ├── similarity >= threshold ──► BLOCK / Policy Action
   │
   └── similarity < threshold ───► ALLOW

Why Use a Similarity Threshold?
Semantic matching produces a similarity score rather than a simple
yes/no result. The threshold defines how strongly the generated response
must match a policy before it is considered a violation.

Example:
Similarity = 0.91
Threshold  = 0.85
Result     = BLOCK

Similarity = 0.72
Threshold  = 0.85
Result     = ALLOW

This allows the system to avoid blocking responses that are only weakly
related to a policy while still catching highly relevant policy violations.

Why Inject PolicyService?
PolicyService is passed into OutputGuardrail instead of being created inside
the class. This follows Dependency Injection principles, reduces coupling,
and makes the guardrail easier to test or replace with another policy
implementation.

Benefits:
- Provides a centralized safety layer for AI-generated output.
- Uses semantic policy matching instead of relying only on keyword rules.
- Supports configurable policy-specific thresholds and actions.
- Reduces false positives by requiring a minimum similarity score.
- Returns structured validation results for logging, auditing, and API handling.
- Keeps policy retrieval separate from policy enforcement through
  Dependency Injection.
"""

class OutputGuardrail:
    def __init__(self, policy_service):
        self.policy_service = policy_service

    async def validate(self, text: str):
        policy = await self.policy_service.find_matching_policy(text)

        # No matching policy
        if not policy:
            return {
                "safe": True,
                "action": "ALLOW",
                "risk_score": 0.0,
            }

        similarity = policy["similarity"]
        threshold = policy["threshold"]

        # Policy violation
        if similarity >= threshold:
            return {
                "safe": False,
                "action": policy["action"],
                "category": policy["category"],
                "risk_score": round(similarity, 4),
                "reason": policy["description"],
                "replacement": (
                    "This response was blocked because "
                    "it may violate corporate compliance policies."
                ),
            }

        return {
            "safe": True,
            "action": "ALLOW",
            "risk_score": round(similarity, 4),
        }