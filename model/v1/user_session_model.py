from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from model.v1.base_env import Base
import uuid


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ✅ Explicit session_id field (unique for each login)
    session_id = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    user_id = Column(BigInteger, nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_used_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_logout_at = Column(DateTime, nullable=True)
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    logs = relationship(
        "UserSessionLog", back_populates="session", cascade="all, delete-orphan"
    )


class UserSessionLog(Base):
    __tablename__ = "user_session_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    session_id = Column(BigInteger, ForeignKey("user_sessions.id", ondelete="CASCADE"))

    jti = Column(
        String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4())
    )
    token_type = Column(String(10), nullable=False)  # 'access' or 'refresh'

    issued_at = Column(DateTime, default=datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)

    ip_address = Column(String(45), nullable=True)
    device_info = Column(Text, nullable=True)

    session = relationship("UserSession", back_populates="logs")
