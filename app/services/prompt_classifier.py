class PromptClassifier:
    def __init__(self):
        self.dev_keywords = {
            "debug",
            "test config",
            "system diagnostic",
            "container status",
            "inspect memory",
        }
        self.admin_keywords = {
            "database count",
            "flush cache",
            "reset server",
            "sudo",
            "system logs",
        }

    def classify(self, prompt: str) -> str:
        if not prompt:
            return "UNKNOWN"

        prompt_lower = prompt.lower()

        # Check for administrative or dev requests
        if any(kw in prompt_lower for kw in self.admin_keywords):
            return "ADMINISTRATIVE"
        if any(kw in prompt_lower for kw in self.dev_keywords):
            return "DEVELOPER_TEST"

        # Support/customer related
        if any(
            kw in prompt_lower
            for kw in [
                "ticket",
                "help",
                "support",
                "refund",
                "issue",
                "problem",
                "error",
                "broken",
                "login",
            ]
        ):
            return "SUPPORT_QUERY"

        return "GENERAL_INQUIRY"


def get_prompt_classifier() -> PromptClassifier:
    return PromptClassifier()
