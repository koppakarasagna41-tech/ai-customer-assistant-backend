import re

class RiskEngine:
    def __init__(self):
        self.security_patterns = r"\b(hack|breach|exploit|unauthorized|leak|vulnerability|malware|compromise|security)\b"
        self.churn_patterns = r"\b(cancel|churn|refund|leaving|quit|stop subscription|chargeback|competitor)\b"
        self.legal_patterns = r"\b(sue|lawsuit|lawyer|legal|compliance|court|gdpr|hipaa|attorney)\b"
        self.outage_patterns = r"\b(down|outage|crash|broken|offline|unusable|stop working)\b"

    def assess_risk(self, text: str, escalation_score: float = 0.0) -> dict:
        if not text:
            return {"level": "LOW", "score": 0.0, "risk_types": []}
            
        text_lower = text.lower()
        score = 0.0
        risk_types = []
        
        if re.search(self.security_patterns, text_lower):
            score += 0.45
            risk_types.append("security")
            
        if re.search(self.legal_patterns, text_lower):
            score += 0.4
            risk_types.append("compliance_legal")
            
        if re.search(self.churn_patterns, text_lower):
            score += 0.25
            risk_types.append("financial_churn")
            
        if re.search(self.outage_patterns, text_lower):
            score += 0.2
            risk_types.append("operational_outage")
            
        # Blend in escalation score
        score += escalation_score * 0.3
        score = round(min(1.0, score), 2)
        
        if score >= 0.7:
            level = "CRITICAL"
        elif score >= 0.4:
            level = "HIGH"
        elif score >= 0.15:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return {
            "level": level,
            "score": score,
            "risk_types": risk_types
        }

def get_risk_engine() -> RiskEngine:
    return RiskEngine()
