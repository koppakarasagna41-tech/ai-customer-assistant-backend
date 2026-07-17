import re

from app.services.pii_detector import PIIDetector, get_pii_detector


class OutputFilter:
    def __init__(self, pii_detector: PIIDetector = None):
        self.pii_detector = pii_detector or get_pii_detector()
        # Look for indicators of prompt leakage, secret credentials, or system errors
        self.leakage_patterns = [
            re.compile(
                r"\b(system_prompt|my\s+instructions\s+are|you\s+are\s+a\s+helpful\s+assistant\s+instructed\s+to|as\s+an\s+ai\s+language\s+model|api[-_]key)\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"\b(password\s*=\s*['\"].*?['\"]|secret_key\s*=\s*['\"].*?['\"])\b", re.IGNORECASE
            ),
        ]

    def filter_response(self, text: str) -> str:
        if not text:
            return ""

        # 1. Mask PII
        masked_text, _ = self.pii_detector.detect_and_mask(text)

        # 2. Look for prompt leakage
        for pattern in self.leakage_patterns:
            if pattern.search(masked_text):
                # Replace leaked prompt signatures with generalized helpful support response
                return (
                    "I can help you address support tickets or answers regarding operations. "
                    "Please let me know how I can assist."
                )

        return masked_text


def get_output_filter() -> OutputFilter:
    return OutputFilter()
