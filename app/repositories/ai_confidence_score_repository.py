from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_confidence_score import (
    AIConfidenceScore as DBAIConfidenceScore,
)
from app.models.ai_confidence_score import (
    AIConfidenceScore,
)


class AIConfidenceScoreRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                
    async def create(
        self,
        confidence: AIConfidenceScore,
    ) -> AIConfidenceScore:
        db_confidence = DBAIConfidenceScore(
            ticket_id=confidence.ticket_id,
            confidence_score=confidence.confidence_score,
            prediction_type=confidence.prediction_type,
            model_name=confidence.model_name,
        )

        self.db.add(db_confidence)
        self.db.commit()
        self.db.refresh(db_confidence)

        return AIConfidenceScore.model_validate(db_confidence)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AIConfidenceScore]:
        scores = (
            self.db.query(DBAIConfidenceScore)
            .filter(DBAIConfidenceScore.ticket_id == ticket_id)
            .order_by(DBAIConfidenceScore.created_at.desc())
            .all()
        )

        return [AIConfidenceScore.model_validate(item) for item in scores]

    async def update(
        self,
        confidence_id: int,
        **kwargs,
    ) -> AIConfidenceScore | None:
        confidence = (
            self.db.query(DBAIConfidenceScore)
            .filter(DBAIConfidenceScore.id == confidence_id)
            .first()
        )

        if not confidence:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(confidence, key, value)

        self.db.commit()
        self.db.refresh(confidence)

        return AIConfidenceScore.model_validate(confidence)

    async def delete(
        self,
        confidence_id: int,
    ) -> bool:
        confidence = (
            self.db.query(DBAIConfidenceScore)
            .filter(DBAIConfidenceScore.id == confidence_id)
            .first()
        )

        if not confidence:
            return False

        self.db.delete(confidence)
        self.db.commit()

        return True


def get_ai_confidence_score_repository() -> AIConfidenceScoreRepository:
    return AIConfidenceScoreRepository()
