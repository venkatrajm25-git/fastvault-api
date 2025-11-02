from functools import wraps
from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from model.v1.audit_log import AuditLog
from sqlalchemy import inspect


def audit_loggable(action, table_name, model_class, id_field: str = None):
    """
    Decorator to log CRUD actions into AuditLog table.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract FastAPI request, db, and current_user if present
            request: Request = kwargs.get("request")
            db: Session = kwargs.get("db")
            current_user = kwargs.get("current_user")

            ip_address = None
            if request:
                ip_address = request.client.host

            performed_by = (
                str(current_user.get("user_id"))
                if current_user and "user_id" in current_user
                else None
            )

            # Capture old data if it's UPDATE or DELETE
            old_data = None
            record_id = None
            if id_field and action in ["UPDATE", "DELETE"]:
                record_id = kwargs.get(id_field)
                if not record_id:
                    # if id is passed inside body instead of kwargs
                    data = kwargs.get("data")
                    if data and hasattr(data, id_field):
                        record_id = getattr(data, id_field)
                if record_id:
                    old_obj = (
                        db.query(model_class)
                        .filter(model_class.id == record_id)
                        .first()
                    )
                    if old_obj:
                        old_data = {
                            c.key: getattr(old_obj, c.key)
                            for c in inspect(old_obj).mapper.column_attrs
                        }

            # Execute main route logic
            response = await func(*args, **kwargs)

            # Capture new data for CREATE or UPDATE
            new_data = None
            changed_fields = None
            if action in ["CREATE", "UPDATE"]:
                try:
                    db_obj = None
                    if action == "CREATE":
                        db_obj = (
                            db.query(model_class)
                            .order_by(model_class.id.desc())
                            .first()
                        )
                    elif record_id:
                        db_obj = (
                            db.query(model_class)
                            .filter(model_class.id == record_id)
                            .first()
                        )

                    if db_obj:
                        new_data = {
                            c.key: getattr(db_obj, c.key)
                            for c in inspect(db_obj).mapper.column_attrs
                        }

                        if old_data:
                            changed_fields = {
                                key: {
                                    "old": old_data.get(key),
                                    "new": new_data.get(key),
                                }
                                for key in new_data.keys()
                                if old_data.get(key) != new_data.get(key)
                            }
                except Exception as e:
                    print(f"[AuditLog Warning] Could not fetch new data: {e}")

            # Create AuditLog record
            try:
                audit_entry = AuditLog(
                    table_name=table_name,
                    record_id=record_id,
                    action=action,
                    changed_fields=changed_fields,
                    old_data=old_data,
                    new_data=new_data,
                    performed_by=performed_by,
                    performed_at=datetime.utcnow(),
                    ip_address=ip_address,
                    module=table_name.split("_")[0].capitalize(),
                    extra_context={"path": str(request.url.path) if request else None},
                )
                db.add(audit_entry)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"[AuditLog Error] Failed to insert log: {e}")

            return response

        return wrapper

    return decorator
