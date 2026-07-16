import re
from typing import Dict, Any
from app.schemas.moderation import ContentModerationResult, ModerationCategory

class ContentModerator:
    def __init__(self):
        # Disallowed topics patterns
        self.policies = {
            "hate_speech": re.compile(r"\b(hate|slur|bigot|discrimination)\b", re.IGNORECASE),
            "harassment": re.compile(r"\b(stalk|harass|abuse|bully)\b", re.IGNORECASE),
            "self_harm": re.compile(r"\b(suicide|self-harm|cut\s+myself|end\s+my\s+life)\b", re.IGNORECASE),
            "sexual_content": re.compile(r"\b(porn|erotic|nsfw|xxx)\b", re.IGNORECASE),
            "violence": re.compile(r"\b(kill|murder|stab|shoot|bomb|attack)\b", re.IGNORECASE),
            "malicious_hacking": re.compile(r"\b(malware|trojan|ransomware|exploit\s+code|sql\s+injection|hack\s+account)\b", re.IGNORECASE)
        }

    def moderate(self, content: str) -> ContentModerationResult:
        if not content:
            return ContentModerationResult(
                flagged=False,
                categories={},
                action_taken="ALLOW",
                filtered_content=""
            )

        categories = {}
        any_flagged = False
        filtered = content
        
        for cat, pattern in self.policies.items():
            match = pattern.search(content)
            flagged = bool(match)
            if flagged:
                any_flagged = True
                # Replace with redacted text
                filtered = pattern.sub("[FILTERED]", filtered)
            
            categories[cat] = ModerationCategory(
                flagged=flagged,
                score=0.95 if flagged else 0.05
            )

        action = "BLOCK" if any_flagged else "ALLOW"
        
        return ContentModerationResult(
            flagged=any_flagged,
            categories=categories,
            action_taken=action,
            filtered_content=filtered
        )

def get_content_moderator() -> ContentModerator:
    return ContentModerator()
