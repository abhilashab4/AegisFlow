class PolicyEngine:

    def __init__(self):
        self.department_policies = {
            "engineering": {
                "allowed_tasks": [
                    "text-summarization",
                    "data-extraction",
                    "code-generation",
                    "complex-reasoning"
                ],
                "allow_endpoints": [
                    "/ai/generate",
                    "/ai/generate-stream"
                ],
                "rate_limit_per_minute": 100
            },
            "finance": {
                "allowed_tasks": [
                    "text-summarization",
                    "data-extraction"
                ],
                "allow_endpoints": [
                    "/ai/generate"
                ],
                "rate_limit_per_minute": 50
            },
            "hr": {
                "allowed_tasks": [
                    "text-summarization"
                ],
                "allow_endpoints": [
                    "/ai/generate"
                ],
                "rate_limit_per_minute": 25
            },
            "compliance": {
                "allowed_tasks": [
                    "text-summarization",
                    "complex-reasoning"
                ],
                "allow_endpoints": [
                    "/ai/generate"
                ],
                "rate_limit_per_minute": 75
            }
        }

        self.task_to_model_mapping = {
            "text-summarization": "llama-3.1-8b-instant",
            "data-extraction": "llama-3.1-8b-instant",
            "complex-reasoning": "llama-3.1-8b-instant",
            "code-generation": "llama-3.1-8b-instant"
        }

    def get_rate_limit(self, department: str):
        policy = self.department_policies.get(department)
        if not policy:
            return 10
        return policy.get("rate_limit_per_minute", 10)

    def is_allowed(self, department: str, endpoint: str, task: str):
        policy = self.department_policies.get(department)

        if not policy:
            return (False, f"Unknown department '{department}'", None)

        if endpoint not in policy["allow_endpoints"]:
            return (False, f"Endpoint not allowed for department '{department}'", None)

        if task not in policy["allowed_tasks"]:
            return (False, f"Task '{task}' is not allowed for department '{department}'", None)

        model = self.task_to_model_mapping.get(task)
        if not model:
            return (False, f"No model mapped for task '{task}'", None)

        return (True, None, model)