from database.v1.seeders.seed_role_permissions import load_yaml, seed_role_permissions
from database.v1.seeders.seed_user_permissions import (
    load_yaml_user_permissions,
    seed_user_permissions,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection


# def run_all_seeders():
#     db_generator = getDBConnection()
#     db = next(db_generator)
#     try:
#         seed_user_permissions(yaml_data, db)

#         db.commit()
#         print("✅ All seeders executed successfully.")
#     except IntegrityError as e:
#         db.rollback()
#         print("⚠️ Error during seeding:", e)


# if __name__ == "__main__":
#     yaml_data = load_yaml("database/v1/seeders/user_permissions.yaml")
#     run_all_seeders()


def run_all_seeders():
    db_generator = getDBConnection()
    db = next(db_generator)
    try:
        seed_role_permissions(yaml_data, db)

        db.commit()
        print("✅ All seeders executed successfully.")
    except IntegrityError as e:
        db.rollback()
        print("⚠️ Error during seeding:", e)


if __name__ == "__main__":
    yaml_data = load_yaml("database/v1/seeders/role_permissions.yaml")
    run_all_seeders()
