from typing import final
from sqlalchemy import Engine, create_engine
from config.v1.config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(Config.DATABASE_URL, echo=False)

Base = declarative_base()

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def getDBConnection():
    db = SessionLocal()
    try:
        db.query()
        yield db
    finally:
        db.close()
