# utils/audit_logger.py
from model.v1.audit_log import AuditLog
from sqlalchemy.orm import Session
from fastapi import Request
from datetime import datetime


# date error : Object of type datetime is not JSON serializable! So serialize data before adding.
def serialize_data(data: dict):
    if not data:
        return data
    return {
        k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in data.items()
    }


async def log_audit(
    db: Session,
    table_name: str,
    record_id: int,
    action: str,
    user: str,
    request: Request,
    old_data: dict = None,
    new_data: dict = None,
):
    # Only show changed fields if UPDATE
    changed_fields = None
    if action == "UPDATE" and old_data and new_data:
        changed_fields = {
            k: {"from": old_data.get(k), "to": new_data.get(k)}
            for k in new_data
            if old_data.get(k) != new_data.get(k)
        }

    ip_address = request.client.host if request else "UNKNOWN"
    module = str(request.url.path) if request else "UNKNOWN"

    audit_entry = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        old_data=serialize_data(old_data),
        new_data=serialize_data(new_data),
        changed_fields=changed_fields,
        performed_by=user,
        ip_address=ip_address,
        module=module,
    )
    db.add(audit_entry)
    db.commit()
