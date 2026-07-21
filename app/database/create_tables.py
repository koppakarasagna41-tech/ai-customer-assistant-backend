from app.database.database import Base, engine

# Import all SQLAlchemy models
from app.db_models.user import User
from app.db_models.ticket  import Ticket
from app.db_models.conversation import Conversation
from app.db_models.analytics import Analytics

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All database tables created successfully!")
