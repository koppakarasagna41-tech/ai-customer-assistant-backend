import re
from typing import Tuple

class InjectionDetector:
    def __init__(self):
        self.patterns = {
            "context_escape": re.compile(
                r"(\]\s*\}\s*---\s*system|\[\s*system\s*update\s*\]|\"\"\"\s*system\s*update|\b(end\s+of\s+conversation|new\s+session|system\s+override)\b)",
                re.IGNORECASE
            ),
            "markdown_html_injection": re.compile(
                r"(<script|javascript:|onload=|onerror=|<iframe|!\[.*?\]\(javascript:|\bmarkdown\s+override\b)",
                re.IGNORECASE
            ),
            "recursive_injection": re.compile(
                r"\b(evaluate\s+the\s+following\s+expression|execute\s+code|run\s+python|eval\(|system\s+instruction\s+injection)\b",
                re.IGNORECASE
            ),
            "rag_poisoning": re.compile(
                r"\b(use\s+only\s+this\s+fake\s+information|ignore\s+knowledge\s+base|poison\s+context|falsify\s+reference)\b",
                re.IGNORECASE
            )
        }

    def detect(self, prompt: str) -> Tuple[bool, float, str, str]:
        if not prompt:
            return False, 0.0, "none", ""

        prompt_lower = prompt.lower()
        
        for name, pattern in self.patterns.items():
            match = pattern.search(prompt_lower)
            if match:
                confidence = 0.85 if name == "context_escape" else 0.75
                return True, confidence, name, match.group(0)

        # Detect excessive brackets or suspicious system role indicators
        if "[system]" in prompt_lower or "role: system" in prompt_lower or "instruction override" in prompt_lower:
            return True, 0.8, "system_role_spoofing", "system instruction headers"

        return False, 0.0, "none", ""

def get_injection_detector() -> InjectionDetector:
    return InjectionDetector()
