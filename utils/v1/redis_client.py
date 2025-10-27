import redis
from typing import Optional
import jwt, time
from config.v1.config import Config

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def redis_set(key: str, value: str, ex: Optional[int] = None):
    return redis_client.set(key, value, ex=ex)


def redis_get(key: str):
    return redis_client.get(key)


def redis_del(key: str):
    return redis_client.delete(key)


def blacklist_token(token: str):
    """Decode token, extract jti & exp, and store it in Redis with TTL."""
    try:
        payload = jwt.decode(
            token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            return

        ttl = max(int(exp - time.time()), 1)  # time left before expiry
        redis_client.set(f"bl:{jti}", "1", ex=ttl)
    except jwt.ExpiredSignatureError:
        # Already expired → no need to blacklist
        pass
    except Exception:
        # Invalid token → skip
        pass


def is_token_blacklisted(jti: str) -> bool:
    """Check if token is blacklisted."""
    return redis_get(f"bl:{jti}") is not None
