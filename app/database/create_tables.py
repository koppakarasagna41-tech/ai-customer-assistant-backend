from app.database.database import Base, engine

# Import all SQLAlchemy models
from app.db_models.user import User
from app.db_models.ticket import Ticket
from app.db_models.ticket_comment import TicketComment
from app.db_models.ticket_timeline import TicketTimeline
from app.db_models.conversation import Conversation
from app.db_models.analytics import Analytics
from app.db_models.attachment import Attachment
from app.db_models.agent import Agent
from app.db_models.assignment_history import AssignmentHistory
from app.db_models.activity_log import ActivityLog
from app.db_models.audit_log import AuditLog
from app.db_models.refresh_token import RefreshToken
from app.db_models.user_preference import UserPreference
from app.db_models.ai_ticket_classification import (
    AITicketClassification,
)
from app.db_models.ai_priority_prediction import (
    AIPriorityPrediction,
)
from app.db_models.ai_suggested_response import (
    AISuggestedResponse,
)
from app.db_models.ai_knowledge_base import (
    AIKnowledgeBase,
)
from app.db_models.ai_conversation_history import (
    AIConversationHistory,
)
from app.db_models.ai_prompt_management import (
    AIPromptManagement,
)
from app.db_models.ai_confidence_score import (
    AIConfidenceScore,
)
from app.db_models.ai_escalation_logic import (
    AIEscalationLogic,
)
# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All database tables created successfully!")
