from datetime import datetime, timedelta
from config.v1.config import Config
import jwt


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return encoded_jwt
