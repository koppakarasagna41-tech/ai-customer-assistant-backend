import re


class LanguageDetector:
    def __init__(self):
        # High frequency unique indicators or stop words for language detection
        self.lang_indicators = {
            "es": r"\b(el|la|los|las|un|una|y|o|en|que|de|por|para|con)\b",
            "fr": r"\b(le|la|les|un|une|et|ou|dans|en|que|de|par|pour|avec)\b",
            "de": r"\b(der|die|das|ein|eine|und|oder|in|dass|von|zu|mit|bei)\b",
            "it": r"\b(il|la|i|gli|un|una|e|o|in|che|di|da|per|con|su)\b",
            "pt": r"\b(o|a|os|as|um|uma|e|ou|em|que|de|por|para|com)\b",
            "ja": r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]",
            "zh": r"[\u4e00-\u9fa5]",
        }

    def detect_language(self, text: str) -> str:
        if not text:
            return "en"
        text_lower = text.lower()
        scores = {"en": 1}  # Base score for English

        for lang, pattern in self.lang_indicators.items():
            matches = re.findall(pattern, text_lower if lang not in ["ja", "zh"] else text)
            if matches:
                scores[lang] = len(matches)

        detected = max(scores, key=scores.get)
        return detected


def get_language_detector() -> LanguageDetector:
    return LanguageDetector()
