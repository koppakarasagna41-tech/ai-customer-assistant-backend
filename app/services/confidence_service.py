from app.schemas.confidence import ConfidenceResponse


class ConfidenceService:
    def calculate_overall_confidence(self, scores: list[float]) -> ConfidenceResponse:
        if not scores:
            return ConfidenceResponse(overall_confidence=1.0, status="HIGH")

        avg_score = sum(scores) / len(scores)
        avg_score = round(avg_score, 2)

        if avg_score >= 0.8:
            status = "HIGH"
        elif avg_score >= 0.5:
            status = "MEDIUM"
        else:
            status = "LOW"

        return ConfidenceResponse(overall_confidence=avg_score, status=status)


def get_confidence_service() -> ConfidenceService:
    return ConfidenceService()
