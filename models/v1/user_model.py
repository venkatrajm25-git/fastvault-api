from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from config.v1.config_dev import Base
from .role_model import Role


class StatusMaster(Base):
    __tablename__ = "status_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False)
    created_by = Column(Integer)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_deleted = Column(Integer, default=0, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), unique=True, nullable=False)
    password = Column(String(200), nullable=False)  # hashed
    user_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("role_master.id"))
    status = Column(Integer, ForeignKey("status_master.id"))
    created_by = Column(Integer)
    modified_by = Column(Integer)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_deleted = Column(Integer, default=0, nullable=False)
