from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from config.v1.config_dev import Base


class Role(Base):
    __tablename__ = "role_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
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
