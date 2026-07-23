import importlib

from app.database.database import Base, engine

# Import all SQLAlchemy model modules to register them with metadata
MODEL_MODULES = [
    "app.db_models.activity_log",
    "app.db_models.agent",
    "app.db_models.ai_confidence_score",
    "app.db_models.ai_conversation_history",
    "app.db_models.ai_escalation_logic",
    "app.db_models.ai_knowledge_base",
    "app.db_models.ai_priority_prediction",
    "app.db_models.ai_prompt_management",
    "app.db_models.ai_suggested_response",
    "app.db_models.ai_ticket_classification",
    "app.db_models.analytics",
    "app.db_models.assignment_history",
    "app.db_models.attachment",
    "app.db_models.audit_log",
    "app.db_models.conversation",
    "app.db_models.notification",
    "app.db_models.refresh_token",
    "app.db_models.ticket",
    "app.db_models.ticket_comment",
    "app.db_models.ticket_timeline",
    "app.db_models.user",
    "app.db_models.user_preference",
]

for module_name in MODEL_MODULES:
    importlib.import_module(module_name)

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All database tables created successfully!")
