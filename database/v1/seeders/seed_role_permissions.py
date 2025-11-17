from os import name
from sqlalchemy.orm import Session
import yaml
from model.v1.module_model import Module
from model.v1.user_model import Role
from model.v1.permission_model import Permission, RolePermission


# Load YAML from file
def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def seed_role_permissions(yaml_data, db: Session):
    try:
        # Step 1: Build valid set from YAML
        valid_permissions = set()

        for role_name, modules in yaml_data.items():
            role = db.query(Role).filter(Role.role_name == role_name).first()
            if not role:
                print(f"Role not found: {role_name}")
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

                    key = (role.id, module.id, permission.id)
                    valid_permissions.add(key)

                    existing = (
                        db.query(RolePermission)
                        .filter_by(
                            role_id=role.id,
                            module_id=module.id,
                            permission_id=permission.id,
                        )
                        .first()
                    )

                    if existing:
                        if existing.is_deleted:
                            existing.is_deleted = 0
                            print(
                                f"♻️ Restored: {role.role_name} → {module.module_name}:{permission.permission_name}"
                            )
                    else:
                        db.add(
                            RolePermission(
                                role_id=role.id,
                                module_id=module.id,
                                permission_id=permission.id,
                                is_deleted=0,
                            )
                        )
                        print(
                            f"✅ Inserted: {role.role_name} → {module.module_name}:{permission.permission_name}"
                        )

        # Step 2: Soft-delete if not in YAML
        all_existing = (
            db.query(RolePermission).filter(RolePermission.is_deleted == 0).all()
        )
        for entry in all_existing:
            key = (entry.role_id, entry.module_id, entry.permission_id)
            if key not in valid_permissions:
                entry.is_deleted = 1
                print(
                    f"🗑️ Marked deleted: role_id={entry.role_id}, module_id={entry.module_id}, permission_id={entry.permission_id}"
                )

        db.commit()
        print("✅ Role permissions synced with YAML.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during role permission seeding: {e}")


# db = getDBConnection()

# if __name__ == "__main__":
#     yaml_data = load_yaml("role_permissions.yaml")
#     seed_role_permissions(yaml_data, db)
