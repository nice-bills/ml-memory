from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- Configuration ---
# We use SQLite for simplicity in Docker/local development.
# The database file will be stored inside the 'data' directory.
# The 'check_same_thread=False' is needed for FastAPI's default worker settings.
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/chat_history.db"

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
