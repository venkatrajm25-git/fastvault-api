from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection
from datetime import datetime
from database.v1.seeders.seed_role_permissions import load_yaml, seed_role_permissions
from database.v1.seeders.seed_user_permissions import (
    load_yaml_user_permissions,
    seed_user_permissions,
)

# Import all your models
from model.v1.module_model import Module
from model.v1.permission_model import Permission
from model.v1.user_model import StatusMaster, Role, User
import sys
import os
from datetime import datetime

from utils.v1.auth_utils import hash_password

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


def safe_add_all(db: Session, records: list):
    for record in records:
        try:
            db.add(record)
            db.flush()  # Flush one by one
            print(f"✅ Seeding done for {record}")
        except IntegrityError as e:
            db.rollback()
            print(f"⚠️ Skipping duplicate or error for record: {record} — {e.orig}")
        else:
            db.commit()


# Seeder functions for all tables
def seed_status_master(db):
    data = [
        StatusMaster(
            id=1, status="Active", created_by=1, created_at=datetime.now(), is_deleted=0
        ),
        StatusMaster(
            id=2,
            status="Inactive",
            created_by=1,
            created_at=datetime.now(),
            is_deleted=0,
        ),
    ]
    safe_add_all(db, data)
    # db.flush()


def seed_roles(db):
    data = [
        Role(
            id=1,
            role_name="Admin",
            status=1,
            created_by=1,
            created_at=datetime.now(),
            is_deleted=0,
        ),
        Role(
            id=2,
            role_name="Manager",
            status=1,
            created_by=1,
            created_at=datetime.now(),
            is_deleted=0,
        ),
        Role(
            id=3,
            role_name="User",
            status=2,
            created_by=1,
            created_at=datetime.now(),
            is_deleted=0,
        ),
    ]
    safe_add_all(db, data)


def seed_users(db):
    data = [
        User(
            id=1,
            email="masteradmin@gmail.com",
            password=hash_password("admin@321"),
            user_name="Admin",
            status=1,
            role_id=1,
            created_by=None,
            modified_by=None,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_deleted=0,
        )
    ]
    safe_add_all(db, data)


def seed_modules(db):
    names = ["Role", "User Management", "RAG Model"]
    data = [
        Module(
            id=i + 1,
            module_name=name,
            created_by=None,
            modified_by=None,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_deleted=0,
        )
        for i, name in enumerate(names)
    ]
    safe_add_all(db, data)


def seed_permissions(db):
    names = ["Create", "Read", "Update", "Delete"]
    modified_bys = [None, 1, None, None]

    data = []
    for i, name in enumerate(names):
        permission = Permission(
            id=i + 1,
            permission_name=name,
            created_by=None,
            modified_by=modified_bys[i],
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_deleted=0,
        )
        data.append(permission)

    safe_add_all(db, data)


# def seed_role_permissions(db):
#     values = [
#         (1, 1, 3, 1),
#         (2, 1, 2, 1),
#         (3, 1, 1, 1),
#         (4, 1, 3, 2),
#         (5, 1, 2, 2),
#         (6, 1, 1, 2),
#         (7, 1, 3, 3),
#         (8, 1, 2, 3),
#     ]
#     data = [
#         RolePermission(
#             id=val[0],
#             role_id=val[1],
#             module_id=val[2],
#             permission_id=val[3],
#             is_deleted=0,
#         )
#         for val in values
#     ]
#     safe_add_all(db, data)


# def seed_user_permissions(db):
#     data = [UserPermission(id=1, user_id=1, module_id=1, permission_id=2, is_deleted=2)]
#     safe_add_all(db, data)


def run_all_seeders():
    db_generator = getDBConnection()
    db = next(db_generator)
    try:
        seed_status_master(db)
        seed_roles(db)
        seed_users(db)
        seed_modules(db)
        seed_permissions(db)
        seed_role_permissions(role_yaml_data, db)
        seed_user_permissions(user_yaml_data, db)
        db.commit()
        print("✅ All seeders executed successfully.")
    except IntegrityError as e:
        db.rollback()
        print("⚠️ Error during seeding:", e)


if __name__ == "__main__":
    role_yaml_data = load_yaml("database/v1/seeders/role_permissions.yaml")
    user_yaml_data = load_yaml_user_permissions(
        "database/v1/seeders/user_permissions.yaml"
    )
    run_all_seeders()
