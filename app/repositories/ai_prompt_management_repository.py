from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_prompt_management import (
    AIPromptManagement as DBAIPromptManagement,
)
from app.models.ai_prompt_management import (
    AIPromptManagement,
)


class AIPromptManagementRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                
    async def create(
        self,
        prompt: AIPromptManagement,
    ) -> AIPromptManagement:
        db_prompt = DBAIPromptManagement(
            prompt_name=prompt.prompt_name,
            prompt_template=prompt.prompt_template,
            prompt_version=prompt.prompt_version,
            model_name=prompt.model_name,
            is_active=prompt.is_active,
        )

        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)

        return AIPromptManagement.model_validate(db_prompt)

    async def get_by_id(
        self,
        prompt_id: int,
    ) -> AIPromptManagement | None:
        prompt = (
            self.db.query(DBAIPromptManagement).filter(DBAIPromptManagement.id == prompt_id).first()
        )

        if not prompt:
            return None

        return AIPromptManagement.model_validate(prompt)

    async def get_all(
        self,
    ) -> list[AIPromptManagement]:
        prompts = self.db.query(DBAIPromptManagement).order_by(DBAIPromptManagement.id.desc()).all()

        return [AIPromptManagement.model_validate(item) for item in prompts]

    async def update(
        self,
        prompt_id: int,
        **kwargs,
    ) -> AIPromptManagement | None:
        prompt = (
            self.db.query(DBAIPromptManagement).filter(DBAIPromptManagement.id == prompt_id).first()
        )

        if not prompt:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(prompt, key, value)

        self.db.commit()
        self.db.refresh(prompt)

        return AIPromptManagement.model_validate(prompt)

    async def delete(
        self,
        prompt_id: int,
    ) -> bool:
        prompt = (
            self.db.query(DBAIPromptManagement).filter(DBAIPromptManagement.id == prompt_id).first()
        )

        if not prompt:
            return False

        self.db.delete(prompt)
        self.db.commit()

        return True


def get_ai_prompt_management_repository() -> AIPromptManagementRepository:
    return AIPromptManagementRepository()
