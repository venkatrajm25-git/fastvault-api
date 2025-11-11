from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
from dao.v1.role_dao import Role_DBConn
import logging

import os
import logging
from logging.handlers import RotatingFileHandler

# Detect environment
is_render = os.getenv("RENDER", "false").lower() == "true"

# Create logger
perm_logger = logging.getLogger("role_services")
perm_logger.setLevel(logging.INFO)

# Common formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

if is_render:
    # ✅ Render → Console logging
    log_handler = logging.StreamHandler()
else:
    # ✅ Local → File logging
    log_dir = "logs/v1"
    os.makedirs(log_dir, exist_ok=True)
    log_handler = RotatingFileHandler(
        f"{log_dir}/role_services.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )

log_handler.setFormatter(formatter)
perm_logger.addHandler(log_handler)


class Role_Services:
    @staticmethod
    async def getRole_serv(role_id, db):
        """Fetches role details based on role_id. Returns all roles if role_id is not provided."""

        def format_role_data(rows):
            return [
                {
                    "id": row.id,
                    "rolename": row.rolename,
                    "status": row.status,
                    "created_by": row.created_by,
                    "modified_by": row.modified_by,
                    "created_at": (
                        row.created_at.isoformat() if row.created_at else None
                    ),
                    "modified_at": (
                        row.modifed_at.isoformat() if row.modifed_at else None
                    ),
                }
                for row in rows
            ]

        logger.info(
            f"Fetching {'all roles' if not role_id else f'role with ID {role_id}'}"
        )

        roles = Role_DBConn.getRoleData(db)
        filtered_roles = (
            roles if not role_id else [role for role in roles if role.id == role_id]
        )

        message_text = (
            "Fetched all roles successfully."
            if not role_id
            else "Fetched single role successfully."
        )

        response = {
            "message": message_text,
            "roles": format_role_data(filtered_roles),
        }

        return JSONResponse(content=response, status_code=200)

    # Returning success status and JSON response

    @staticmethod
    async def updateRole_serv(dataList, db):
        """Updates role details including rolename, status, and modified_by."""
        role_id, rolename, status, modified_by = dataList
        logger.info(f"Updating role details for role_id: {role_id}")

        rolename = rolename or None
        status = status or None

        existing_role = next(
            (r for r in Role_DBConn.getRoleData(db) if r.id == role_id), None
        )
        if not existing_role:
            logger.warning(f"No data found for role_id: {role_id}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Role not found.",
                },
                status_code=400,
            )

        updates = {
            "rolename": rolename if rolename != existing_role.rolename else None,
            "status": status if status != existing_role.status else None,
            "modified_by": (
                modified_by if modified_by != existing_role.modified_by else None
            ),
        }
        updates = {k: v for k, v in updates.items() if v is not None}

        # Step 5: Perform Update
        success = Role_DBConn.updateRoleDB(
            role_id, list(updates.keys()), list(updates.values()), db
        )

        # Step 6: Return Response
        if success:
            logger.info(f"Role ID {role_id} updated successfully.")
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Role updated successfully.",
                    "updated": [
                        {
                            "role_id": role_id,
                            "rolename": updates.get("rolename", existing_role.rolename),
                            "status": updates.get("status", existing_role.status),
                            "modified_by": updates.get(
                                "modified_by", existing_role.modified_by
                            ),
                        }
                    ],
                },
                status_code=200,
            )

        logger.error(f"Failed to update role_id: {role_id}")
        return JSONResponse(
            content={
                "success": False,
                "message": "Role update failed.",
            },
            status_code=400,
        )
