import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    print("Connected.")
except Exception as e:
    print("Failed", str(e))
