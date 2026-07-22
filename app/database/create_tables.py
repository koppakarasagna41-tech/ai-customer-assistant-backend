from app.database.database import Base, engine

# Import all SQLAlchemy models

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All database tables created successfully!")
