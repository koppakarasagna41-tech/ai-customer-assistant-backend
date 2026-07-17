import re
import unicodedata


class PromptSanitizer:
    def __init__(self):
        # Hidden control characters, backspaces, strange unicode spaces
        self.control_chars_pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
        self.whitespace_pattern = re.compile(r"\s+")

    def normalize(self, prompt: str) -> tuple[str, dict]:
        if not prompt:
            return "", {
                "original_length": 0,
                "cleaned_length": 0,
                "unicode_normalized": True,
                "hidden_chars_removed": 0,
            }

        original_len = len(prompt)
        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", prompt)

        # 2. Hidden characters removal
        cleaned = self.control_chars_pattern.sub("", normalized)
        hidden_removed = original_len - len(cleaned)

        # 3. Collapse whitespace
        cleaned = self.whitespace_pattern.sub(" ", cleaned).strip()

        details = {
            "original_length": original_len,
            "cleaned_length": len(cleaned),
            "unicode_normalized": True,
            "hidden_chars_removed": hidden_removed,
        }
        return cleaned, details

    def sanitize(self, prompt: str) -> str:
        # Simple sanitization - strip unsafe script/html tags if present to
        # prevent HTML/JS injection
        cleaned = re.sub(r"<script.*?>.*?</script>", "", prompt, flags=re.IGNORECASE)
        cleaned = re.sub(r"<iframe.*?>.*?</iframe>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"javascript:", "", cleaned, flags=re.IGNORECASE)
        return cleaned


def get_prompt_sanitizer() -> PromptSanitizer:
    return PromptSanitizer()
