class PolicyEngine:

    def __init__(self):

        self.role_policies = {
            "admin": {
                "allowed_tasks": ["*"],
                "allow_endpoints": ["*"]
            },

            "employee": {
                "allowed_tasks": ["text-summarization", "data-extraction", "code-generation"],
                "allow_endpoints": ["/ai/generate", "/ai/generate-stream"]
            },

            "analyst": {
                "allowed_tasks": ["text-summarization", "complex-reasoning", "data-extraction"],
                "allow_endpoints": ["/ai/generate"]
            },

            "intern": {
                "allowed_tasks": ["text-summarization"],
                "allow_endpoints": ["/ai/generate"]
            }
        }

        self.task_to_model_mapping = {
            "text-summarization": "llama-3.1-8b-instant",
            "data-extraction": "llama-3.1-8b-instant",
            "complex-reasoning": "llama-3.1-8b-instant",
            "code-generation": "llama-3.1-8b-instant"
        }

    def is_allowed(self, role: str, endpoint: str, task: str):

        policy = self.role_policies.get(role)

        if not policy:
            return False, "Unknown role", None

        if "*" not in policy["allow_endpoints"] and endpoint not in policy["allow_endpoints"]:
            return False, f"Endpoint not allowed for role {role}", None

        allowed_tasks = policy["allowed_tasks"]

        if "*" in allowed_tasks:
            resolved_model = self.task_to_model_mapping.get(task, "llama-3.1-8b-instant")
            return True, None, resolved_model

        if task not in allowed_tasks:
            return False, f"Task '{task}' is not permitted for role {role}", None

        resolved_model = self.task_to_model_mapping.get(task)

        if not resolved_model:
            return False, f"Task '{task}' is recognized but has no model mapped to it", None

        return True, None, resolved_model