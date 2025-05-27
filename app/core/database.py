"""
Handle the database connection and session management.
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create a database engine
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """
    Initialize the database by creating the tables.

    This function should be called once on application startup.
    """
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    """
    Yield a database session to be used in a context manager.

    This function returns a generator that yields a database session.
    The session is automatically closed when the context manager is exited.
    """
    with Session(engine) as session:
        yield session
