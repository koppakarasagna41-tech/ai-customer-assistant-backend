import re
from typing import Tuple

class JailbreakDetector:
    def __init__(self):
        self.patterns = {
            "developer_override": re.compile(
                r"\b(ignore\s+(all\s+)?instructions|developer\s+mode|override\s+rules|bypass\s+safety|developer\s+override|sudo\s+override)\b",
                re.IGNORECASE
            ),
            "role_reversal": re.compile(
                r"\b(pretend\s+to\s+be|you\s+are\s+now|act\s+as|roleplay|hypothetical\s+scenario\s+where\s+you|dan\s+mode|do\s+anything\s+now)\b",
                re.IGNORECASE
            ),
            "system_leakage": re.compile(
                r"\b(reveal\s+your\s+system\s+prompt|what\s+is\s+your\s+instruction|print\s+instructions\s+above|output\s+the\s+preceding\s+text|show\s+your\s+guidelines)\b",
                re.IGNORECASE
            ),
            "obfuscation_jailbreak": re.compile(
                r"\b(decode\s+this\s+base64|rot13|caesar\s+cipher|translate\s+from\s+leet|cipher\s+text)\b",
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
                # Assign confidence and return
                confidence = 0.9 if name in ["developer_override", "role_reversal"] else 0.8
                return True, confidence, name, match.group(0)
                
        # Subtle heuristic: repeated instruction imperatives
        if prompt_lower.count("ignore") > 1 and "instruction" in prompt_lower:
            return True, 0.75, "instruction_manipulation", "multiple ignore statements"

        return False, 0.0, "none", ""

def get_jailbreak_detector() -> JailbreakDetector:
    return JailbreakDetector()
