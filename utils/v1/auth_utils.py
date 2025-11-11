import bcrypt
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from model.v1.user_model import PasswordResetToken


def hash_password(password: str) -> str:
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


async def verifyResetPassToken(raw_token, db: Session):
    tokens_from_db = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .all()
    )

    valid_token = None
    for t in tokens_from_db:
        if verify_password(raw_token, t.token):
            valid_token = t
            break

    if not valid_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return valid_token
