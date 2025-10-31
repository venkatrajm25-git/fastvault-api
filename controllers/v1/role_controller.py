from services.v1.role_services import Role_Services
from utils.v1.lang_utils import translate, translate_many, translate_pair

# from helpers.v1.role_helpers import verifyRoleID
from dao.v1.role_dao import Role_DBConn
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
from model.v1.user_model import Role
from sqlalchemy.orm import Session
import logging


log_handler = RotatingFileHandler(
    "logs/v1/role_controller.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

role_logger = logging.getLogger("role_logger")
role_logger.setLevel(logging.INFO)
role_logger.addHandler(log_handler)


class RoleController:
    @staticmethod
    async def getRole(role_id, db, accept_language):
        """Retrieves details of a specific role based on role ID."""
        try:
            role_logger.info(f"Fetching role details: RoleID={role_id}")

            # Call service layer to fetch role details
            result = await Role_Services.getRole_serv(role_id, db, accept_language)
            return result
        except Exception as e:
            role_logger.error(f"error: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    def addrole(data, db, accept_language, current_user):
        """Adds a new role to the system."""
        try:
            rolename = data.get("rolename").strip()  # Get and clean role name
            status = (
                str(data.get("status")).strip() if data.get("status") else ""
            )  # Get and clean role status
            created_by = current_user["user_id"]

            if not rolename:
                return JSONResponse(
                    content={
                        "success": "false",
                        translate("message", lang=accept_language): translate_many(
                            ["rolename", "is_missing"],
                            lang=accept_language,
                        ),
                    },
                    status_code=400,
                )

            role_logger.info(
                f"Adding new role: Name={rolename}, Created By={created_by}"
            )

            # Check if the role already exists
            existing_roles = Role_DBConn.getRoleData(db)
            for role in existing_roles:
                if role.rolename == rolename:
                    role_logger.warning(
                        f"Role creation failed: Role {rolename} already exists."
                    )
                    return JSONResponse(
                        content={
                            **translate_pair("success", "false", lang=accept_language),
                            **translate_pair(
                                "message",
                                translate_many(
                                    ["rolename", "already_exists"],
                                    lang=accept_language,
                                ),
                            ),
                        },
                        status_code=400,
                    )

            # Add role to the database
            dataList = [rolename, status, created_by]
            result = Role_DBConn.createRole(dataList, db)
            if isinstance(result, bool):
                role_logger.info(f"Role '{rolename}' Created successfully")
                return JSONResponse(
                    content={
                        **translate_pair("success", "true", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["role", "created_successfully"], lang=accept_language
                        ),
                        "data": [
                            {
                                "rolename": rolename,
                                "status": status,
                                "created_by": created_by,
                            }
                        ],
                    },
                    status_code=201,
                )
            else:
                role_logger.warning(f"Role creation failed")
                return result

        except Exception as e:
            role_logger.error(f"error: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateRole(data, db, accept_language, current_user):
        """Updates an existing role in the system."""
        try:
            role_logger.info(f"updateRole called with data: {data}")

            role_id = data.role_id
            modified_by = current_user["user_id"]

            # Debug logs to confirm execution
            role_logger.info(f"Received role_id: {role_id}")

            rolename = data.rolename.strip()  # Get new role name
            status = data.status

            dataList = [role_id, rolename, status, modified_by]

            # Call service layer to update role
            result = await Role_Services.updateRole_serv(dataList, db, accept_language)
            return result
        except Exception as e:
            role_logger.error(f"error: {e}")
            return JSONResponse(
                content={
                    "success": False,
                    translate("message", lang=accept_language): str(e),
                },
                status_code=400,
            )

    @staticmethod
    async def deleteRole(role_id, db: Session, accept_language):
        """Deletes an existing role from the system."""
        try:
            role_logger.info(f"deleteRole called with role_id: {role_id}")

            # Verify if the role ID exists
            # roleIDverification = await verifyRoleID(role_id, db, accept_language)
            # if roleIDverification.status_code == 400:
            #     role_logger.warning(
            #         f"Invalid role_id: {role_id}"
            #     )  # Logging warning if role_id is invalid
            #     return roleIDverification

            # Perform delete operation

            db.query(Role).filter(Role.id == role_id).update({"is_deleted": 1})
            db.commit()
            role_logger.info(f"Role deleted successfully: {role_id}")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["role", "deleted_successfully"]
                    ),
                },
                status_code=200,
            )
        except Exception as e:
            role_logger.error(f"error: {e}")
            return JSONResponse(
                content={
                    **translate_pair("success", "false", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["role", "deletion_failed"]
                    ),
                },
                status_code=400,
            )
