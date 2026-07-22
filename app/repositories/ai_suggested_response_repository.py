from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_suggested_response import (
    AISuggestedResponse as DBAISuggestedResponse,
)
from app.models.ai_suggested_response import (
    AISuggestedResponse,
)


class AISuggestedResponseRepository:
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
        response: AISuggestedResponse,
    ) -> AISuggestedResponse:
        db_response = DBAISuggestedResponse(
            ticket_id=response.ticket_id,
            suggested_response=response.suggested_response,
            confidence_score=response.confidence_score,
            model_name=response.model_name,
            prompt_version=response.prompt_version,
            status=response.status,
        )

        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)

        return AISuggestedResponse.model_validate(
            db_response
        )

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> AISuggestedResponse | None:
        response = (
            self.db.query(DBAISuggestedResponse)
            .filter(
                DBAISuggestedResponse.ticket_id == ticket_id
            )
            .first()
        )

        if not response:
            return None

        return AISuggestedResponse.model_validate(
            response
        )

    async def update(
        self,
        ticket_id: str,
        **kwargs,
    ) -> AISuggestedResponse | None:
        response = (
            self.db.query(DBAISuggestedResponse)
            .filter(
                DBAISuggestedResponse.ticket_id == ticket_id
            )
            .first()
        )

        if not response:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(response, key, value)

        self.db.commit()
        self.db.refresh(response)

        return AISuggestedResponse.model_validate(
            response
        )

    async def delete(
        self,
        ticket_id: str,
    ) -> bool:
        response = (
            self.db.query(DBAISuggestedResponse)
            .filter(
                DBAISuggestedResponse.ticket_id == ticket_id
            )
            .first()
        )

        if not response:
            return False

        self.db.delete(response)
        self.db.commit()

        return True


def get_ai_suggested_response_repository() -> (
    AISuggestedResponseRepository
):
    return AISuggestedResponseRepository()