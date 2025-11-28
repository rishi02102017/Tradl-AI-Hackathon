"""Initialize the database."""
import os
from sqlalchemy import create_engine
from src.database.models import Base

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_news.db")

def init_database():
    """Initialize the database with all tables."""
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DATABASE_URL}")

if __name__ == "__main__":
    init_database()

