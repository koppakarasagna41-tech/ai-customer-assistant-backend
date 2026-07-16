import re
from typing import Tuple, List

class PIIDetector:
    def __init__(self):
        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
            "api_key": re.compile(r"\b(AIzaSy[A-Za-z0-9-_]{35}|sk-[A-Za-z0-9]{32,48})\b"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        }

    def detect_and_mask(self, text: str) -> Tuple[str, List[str]]:
        if not text:
            return "", []

        masked_text = text
        detected_types = []
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(masked_text)
            if matches:
                detected_types.append(pii_type)
                masked_text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", masked_text)
                
        return masked_text, detected_types

def get_pii_detector() -> PIIDetector:
    return PIIDetector()
