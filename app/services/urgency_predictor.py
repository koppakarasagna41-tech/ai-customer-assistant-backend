import re

class UrgencyPredictor:
    def __init__(self):
        self.critical_patterns = [
            r"\b(production down|prod down|outage|system down|cannot login|critical issue|broken|crash)\b",
            r"\b(immediately|urgent|asap|priority 1|p1|emergency|as soon as possible)\b",
            r"\b(losing money|legal|lawsuit|furious|disaster|catastrophe)\b"
        ]
        self.medium_patterns = [
            r"\b(error|bug|fail|failed|issue|problem|invoice|billing|not working|cannot find|wrong)\b",
            r"\b(question|help|support|request|how to|clarification)\b"
        ]

    def predict_urgency(self, text: str, sentiment_score: float = 0.5) -> dict:
        if not text:
            return {"level": "low", "score": 0.0}
            
        text_lower = text.lower()
        score = 0.0
        
        # Heuristic pattern matching
        for pattern in self.critical_patterns:
            if re.search(pattern, text_lower):
                score += 0.4
                
        for pattern in self.medium_patterns:
            if re.search(pattern, text_lower):
                score += 0.15
                
        # Blend in sentiment intensity
        if sentiment_score > 0.7:
            score += 0.2
            
        score = round(min(1.0, score), 2)
        
        if score >= 0.7:
            level = "high"
        elif score >= 0.35:
            level = "medium"
        else:
            level = "low"
            
        return {"level": level, "score": score}

def get_urgency_predictor() -> UrgencyPredictor:
    return UrgencyPredictor()
