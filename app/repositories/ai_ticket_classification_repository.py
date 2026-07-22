from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_ticket_classification import (
    AITicketClassification as DBAITicketClassification,
)
from app.models.ai_ticket_classification import (
    AITicketClassification,
)


class AITicketClassificationRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception:
                pass

    async def create(
        self,
        classification: AITicketClassification,
    ) -> AITicketClassification:
        db_classification = DBAITicketClassification(
            ticket_id=classification.ticket_id,
            predicted_category=classification.predicted_category,
            confidence_score=classification.confidence_score,
            model_name=classification.model_name,
            prompt_version=classification.prompt_version,
            raw_response=classification.raw_response,
        )

        self.db.add(db_classification)
        self.db.commit()
        self.db.refresh(db_classification)

        return AITicketClassification.model_validate(
            db_classification
        )

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> AITicketClassification | None:
        classification = (
            self.db.query(DBAITicketClassification)
            .filter(
                DBAITicketClassification.ticket_id == ticket_id
            )
            .first()
        )

        if not classification:
            return None

        return AITicketClassification.model_validate(
            classification
        )

    async def update(
        self,
        ticket_id: str,
        **kwargs,
    ) -> AITicketClassification | None:
        classification = (
            self.db.query(DBAITicketClassification)
            .filter(
                DBAITicketClassification.ticket_id == ticket_id
            )
            .first()
        )

        if not classification:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(classification, key, value)

        self.db.commit()
        self.db.refresh(classification)

        return AITicketClassification.model_validate(
            classification
        )

    async def delete(
        self,
        ticket_id: str,
    ) -> bool:
        classification = (
            self.db.query(DBAITicketClassification)
            .filter(
                DBAITicketClassification.ticket_id == ticket_id
            )
            .first()
        )

        if not classification:
            return False

        self.db.delete(classification)
        self.db.commit()

        return True


def get_ai_ticket_classification_repository() -> (
    AITicketClassificationRepository
):
    return AITicketClassificationRepository()