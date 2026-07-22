from datetime import UTC, datetime

from app.models.ai_prompt_management import (
    AIPromptManagement,
)
from app.repositories.ai_prompt_management_repository import (
    AIPromptManagementRepository,
    get_ai_prompt_management_repository,
)
from app.schemas.ai_prompt_management import (
    AIPromptManagementCreate,
    AIPromptManagementUpdate,
)


class AIPromptManagementService:
    def __init__(
        self,
        repository: AIPromptManagementRepository | None = None,
    ):
        self.repository = (
            repository
            if repository
            else get_ai_prompt_management_repository()
        )

    async def create_prompt(
        self,
        data: AIPromptManagementCreate,
    ) -> AIPromptManagement:
        prompt = AIPromptManagement(
            id=0,
            prompt_name=data.prompt_name,
            prompt_template=data.prompt_template,
            prompt_version=data.prompt_version,
            model_name=data.model_name,
            is_active=data.is_active,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(prompt)

    async def get_prompt(
        self,
        prompt_id: int,
    ) -> AIPromptManagement | None:
        return await self.repository.get_by_id(
            prompt_id
        )

    async def get_all_prompts(
        self,
    ) -> list[AIPromptManagement]:
        return await self.repository.get_all()

    async def update_prompt(
        self,
        prompt_id: int,
        data: AIPromptManagementUpdate,
    ) -> AIPromptManagement | None:
        return await self.repository.update(
            prompt_id,
            prompt_name=data.prompt_name,
            prompt_template=data.prompt_template,
            prompt_version=data.prompt_version,
            model_name=data.model_name,
            is_active=data.is_active,
        )

    async def delete_prompt(
        self,
        prompt_id: int,
    ) -> bool:
        return await self.repository.delete(
            prompt_id
        )


def get_ai_prompt_management_service() -> (
    AIPromptManagementService
):
    return AIPromptManagementService()