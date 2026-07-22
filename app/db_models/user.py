from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, String

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String(50), default="customer")
    permissions = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
