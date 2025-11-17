from model.v1.user_model import User
from model.v1.module_model import Module
from model.v1.permission_model import Permission, UserPermission
import yaml


def load_yaml_user_permissions(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def seed_user_permissions(yaml_data, db):
    try:
        # Step 1: Build valid set from YAML
        valid_permissions = set()
        for email, modules in yaml_data.items():
            user = db.query(User).filter(User.email == email).first()
            if not user:
                print(f"User not found: {email}")
                continue

            for module_name, actions in modules.items():
                module = (
                    db.query(Module).filter(Module.module_name == module_name).first()
                )
                if not module:
                    print(f"Module not found: {module_name}")
                    continue

                for action_name in actions:
                    permission = (
                        db.query(Permission)
                        .filter(Permission.permission_name == action_name)
                        .first()
                    )
                    if not permission:
                        print(f"Permission not found: {action_name}")
                        continue

                    valid_permissions.add((user.id, module.id, permission.id))

                    # Insert or restore
                    existing = (
                        db.query(UserPermission)
                        .filter_by(
                            user_id=user.id,
                            module_id=module.id,
                            permission_id=permission.id,
                        )
                        .first()
                    )

                    if existing:
                        if existing.is_deleted:
                            existing.is_deleted = 0
                            print(
                                f"♻️ Restored: {email} → {module.module_name}:{permission.permission_name}"
                            )
                    else:
                        db.add(
                            UserPermission(
                                user_id=user.id,
                                module_id=module.id,
                                permission_id=permission.id,
                                is_deleted=0,
                            )
                        )
                        print(
                            f"✅ Inserted: {email} → {module.module_name}:{permission.permission_name}"
                        )

        # Step 2: Mark as deleted if not in YAML
        all_existing = (
            db.query(UserPermission).filter(UserPermission.is_deleted == 0).all()
        )
        for entry in all_existing:
            key = (entry.user_id, entry.module_id, entry.permission_id)
            if key not in valid_permissions:
                entry.is_deleted = 1
                print(
                    f"🗑️ Marked deleted: user_id={entry.user_id}, module_id={entry.module_id}, permission_id={entry.permission_id}"
                )

        db.commit()
        print("✅ User permissions synced with YAML.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during user permission seeding: {e}")
