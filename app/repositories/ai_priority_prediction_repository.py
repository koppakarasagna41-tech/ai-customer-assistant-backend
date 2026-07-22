from sqlalchemy.orm import Session
from contextlib import suppress
from app.database.database import SessionLocal
from app.db_models.ai_priority_prediction import (
    AIPriorityPrediction as DBAIPriorityPrediction,
)
from app.models.ai_priority_prediction import (
    AIPriorityPrediction,
)


class AIPriorityPredictionRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(
        self,
        prediction: AIPriorityPrediction,
    ) -> AIPriorityPrediction:
        db_prediction = DBAIPriorityPrediction(
            ticket_id=prediction.ticket_id,
            predicted_priority=prediction.predicted_priority,
            confidence_score=prediction.confidence_score,
            model_name=prediction.model_name,
            prompt_version=prediction.prompt_version,
            raw_response=prediction.raw_response,
        )

        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)

        return AIPriorityPrediction.model_validate(db_prediction)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> AIPriorityPrediction | None:
        prediction = (
            self.db.query(DBAIPriorityPrediction)
            .filter(DBAIPriorityPrediction.ticket_id == ticket_id)
            .first()
        )

        if not prediction:
            return None

        return AIPriorityPrediction.model_validate(prediction)

    async def update(
        self,
        ticket_id: str,
        **kwargs,
    ) -> AIPriorityPrediction | None:
        prediction = (
            self.db.query(DBAIPriorityPrediction)
            .filter(DBAIPriorityPrediction.ticket_id == ticket_id)
            .first()
        )

        if not prediction:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(prediction, key, value)

        self.db.commit()
        self.db.refresh(prediction)

        return AIPriorityPrediction.model_validate(prediction)

    async def delete(
        self,
        ticket_id: str,
    ) -> bool:
        prediction = (
            self.db.query(DBAIPriorityPrediction)
            .filter(DBAIPriorityPrediction.ticket_id == ticket_id)
            .first()
        )

        if not prediction:
            return False

        self.db.delete(prediction)
        self.db.commit()

        return True


def get_ai_priority_prediction_repository() -> AIPriorityPredictionRepository:
    return AIPriorityPredictionRepository()
