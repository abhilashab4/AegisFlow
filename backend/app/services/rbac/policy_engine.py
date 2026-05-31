class PolicyEngine:

    def __init__(self):

        self.role_policies = {
            "admin": {
                "allow_models": ["*"],
                "allow_endpoints": ["*"]
            },

            "employee": {
                "allow_models": ["llama-3.1-8b-instant"],
                "allow_endpoints": ["/ai/generate", "/ai/generate-stream"]
            },

            "analyst": {
                "allow_models": ["llama-3.1-8b-instant"],
                "allow_endpoints": ["/ai/generate", "/ai/generate-stream"]
            },

            "intern": {
                "allow_models": [],
                "allow_endpoints": []
            }
        }

    def is_allowed(self, role: str, endpoint: str, model: str):

        policy = self.role_policies.get(role)

        if not policy:
            return False, "Unknown role"

        if "*" not in policy["allow_endpoints"] and endpoint not in policy["allow_endpoints"]:
            return False, f"Endpoint not allowed for role {role}"

        if "*" not in policy["allow_models"] and model not in policy["allow_models"]:
            return False, f"Model not allowed for role {role}"

        return True, None