import re

class MessageNormalizer:
    def normalize(self, text: str) -> str:
        if not text:
            return ""
        # 1. Remove duplicate spaces
        text = re.sub(r'\s+', ' ', text)
        # 2. Trim whitespace
        text = text.strip()
        # 3. Remove non-printable control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        return text

    def detect_message_type(self, text: str) -> str:
        # Detect if it is conversational, technical/code, or transactional
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|\{.*\}|\[.*\]|import |def |class |const |function)', text, re.IGNORECASE):
            return "technical_code"
        elif re.search(r'(invoice|INV-|billing|charge|payment|refund|transaction)', text, re.IGNORECASE):
            return "transactional"
        return "conversational"


def get_message_normalizer() -> MessageNormalizer:
    return MessageNormalizer()
