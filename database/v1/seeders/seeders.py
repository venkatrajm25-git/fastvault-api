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
from model.v1.perm_model import Permission
from model.v1.user_model import StatusMaster, Role, Users
import sys
import os

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
            id=1,
            status="Active",
            created_by=1,
            modified_by=None,
            created_at=datetime(2025, 6, 16, 12, 10, 34),
            modified_at=datetime(2025, 6, 16, 12, 10, 34),
        ),
        StatusMaster(
            id=2,
            status="Inactive",
            created_by=1,
            modified_by=None,
            created_at=datetime(2025, 6, 16, 12, 10, 34),
            modified_at=datetime(2025, 6, 16, 12, 10, 34),
        ),
    ]
    safe_add_all(db, data)
    # db.flush()


def seed_roles(db):
    data = [
        Role(
            id=1,
            rolename="Admin",
            status=1,
            created_by=1,
            created_at=datetime(2025, 6, 16, 12, 9, 8),
            is_deleted=0,
        ),
        Role(
            id=2,
            rolename="Manager",
            status=1,
            created_by=1,
            created_at=datetime(2025, 6, 16, 12, 9, 27),
            is_deleted=0,
        ),
        Role(
            id=3,
            rolename="User",
            status=2,
            created_by=1,
            created_at=datetime(2025, 6, 16, 12, 9, 44),
            is_deleted=0,
        ),
    ]
    safe_add_all(db, data)


def seed_users(db):
    data = [
        Users(
            id=1,
            email="admin@jeenox.com",
            pwd="$2b$12$WRa4x/BEDfxYbmmpE3zbSenttknQpDUWr.XTTSttEbjDxwq6NnjI2",
            username="Admin JeenoX",
            status=1,
            role=1,
            created_by=1,
            modified_by=1,
            created_at=datetime(2025, 6, 16, 12, 10, 37),
            modified_at=datetime(2025, 7, 3, 19, 32, 57),
            is_deleted=0,
        ),
        Users(
            id=2,
            email="manager@jeenox.com",
            pwd="$2b$12$h0ncleKnEYtg7GjsQmlFEeJR0FtIRovNCbOVvmehO8/KqXAwhr6UC",
            username="Manager",
            status=1,
            role=2,
            created_by=1,
            modified_by=1,
            created_at=datetime(2025, 7, 3, 18, 35, 7),
            modified_at=datetime(2025, 7, 8, 12, 46, 48),
            is_deleted=0,
        ),
        Users(
            id=3,
            email="user@jeenox.com",
            pwd="$2b$12$xs5bGflNIgM4/zNg5ZDm6uSyMJsRShaRSQkoME9XI/WFt0C5cEAvi",
            username="User",
            status=1,
            role=3,
            created_by=1,
            modified_by=1,
            created_at=datetime(2025, 7, 3, 18, 35, 7),
            modified_at=datetime(2025, 7, 8, 12, 46, 48),
            is_deleted=0,
        ),
    ]
    safe_add_all(db, data)


def seed_modules(db):
    names = ["Role", "User Management", "RAG Model"]
    data = [
        Module(
            id=i + 1,
            name=name,
            created_by=None,
            modified_by=None,
            created_at=datetime(2025, 6, 16, 12, 35, 45),
            modified_at=datetime(2025, 6, 16, 12, 35, 45),
            is_deleted=0,
        )
        for i, name in enumerate(names)
    ]
    safe_add_all(db, data)


def seed_permissions(db):
    names = ["Create", "Read", "Update", "Delete"]
    modified_bys = [None, 1, None, None]
    modified_ats = [
        datetime(2025, 6, 16, 12, 34, 15),
        datetime(2025, 7, 2, 17, 58, 25),
        datetime(2025, 6, 16, 12, 34, 15),
        datetime(2025, 6, 16, 12, 34, 15),
    ]
    data = [
        Permission(
            id=i + 1,
            name=name,
            created_by=None,
            modified_by=modified_bys[i],
            created_at=datetime(2025, 6, 16, 12, 34, 15),
            modified_at=modified_ats[i],
            is_deleted=0,
        )
        for i, name in enumerate(names)
    ]
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
