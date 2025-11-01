from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from config.v1.config_dev import Base
from sqlalchemy import UniqueConstraint


class Permission(Base):
    __tablename__ = "permission_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_name = Column(String(100), nullable=False, unique=True)
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


class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("role_master.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission_master.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("module_master.id"), nullable=False)
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

    __table_args__ = (
        UniqueConstraint(
            "role_id", "permission_id", "module_id", name="uix_role_permission"
        ),
    )


class UserPermission(Base):
    __tablename__ = "user_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission_master.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("module_master.id"), nullable=False)
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

    __table_args__ = (
        UniqueConstraint(
            "user_id", "permission_id", "module_id", name="uix_user_permission"
        ),
    )
