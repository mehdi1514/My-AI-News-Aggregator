import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    # to connect to local db
    # user = os.getenv("POSTGRES_USER", "postgres")
    # password = os.getenv("POSTGRES_PASSWORD", "postgres")
    # host = os.getenv("POSTGRES_HOST", "localhost")
    # port = os.getenv("POSTGRES_PORT", "5432")
    # db = os.getenv("POSTGRES_DATABASE", "ai_news_aggregator")

    # to connect to remote db
    url = os.getenv("POSTGRES_URL")
    return url

engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

