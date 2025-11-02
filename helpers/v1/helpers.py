from model.v1.user_model import Role, User
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime

# import pytest


class IDGeneration:
    def userID(db: Session) -> int:
        last_id = db.query(func.max(User.id)).scalar()
        return (last_id or 0) + 1


def serialize_data(data: dict):
    if not data:
        return data
    return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in data.items()}
