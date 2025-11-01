from sqlalchemy import Column, Integer, String, Enum, JSON, DateTime
from sqlalchemy.sql import func
from model.v1.base_env import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    action = Column(
        Enum("LOGIN", "LOGOUT", "CHANGE_PASSWORD", "CREATE", "UPDATE", "DELETE"),
        nullable=False,
    )
    changed_fields = Column(JSON)
    old_data = Column(JSON)
    new_data = Column(JSON)
    performed_by = Column(String(100), nullable=False)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    module = Column(String(100))
    extra_context = Column(JSON)
