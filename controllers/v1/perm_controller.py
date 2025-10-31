from helpers.v1.permission_helpers import (
    verifyModuleRolendPermID,
    verifyModuleUserndPermID,
)

from model.v1.module_model import Module
from model.v1.perm_model import Permission, RolePermission, UserPermission
from utils.v1.lang_utils import translate, translate_many, translate_pair
from services.v1.permission_services import Perm_Serv, Module_Serv
from dao.v1.perm_dao import RolePerm_DBConn, UserPerm_DBConn
from dao.v1.user_dao import user_databaseConnection
from dao.v1.module_dao import Module_DBConn
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
from collections import defaultdict
import logging


# Configure rotating log handler for user activity
log_handler = RotatingFileHandler(
    "logs/v1/perm_controller.log", maxBytes=5 * 1024 * 1024, backupCount=5
)  # 5MB max per file, keeps 5 backups

log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

# Get logger and attach handler
perm_logger = logging.getLogger("perm_logger")
perm_logger.setLevel(logging.INFO)
perm_logger.addHandler(log_handler)


class PermissionModule:
    @staticmethod
    async def getRolePermission(role_id, db, accept_language):
        perm_logger.info("Fetching role permissions from the database.")
        try:
            data = RolePerm_DBConn.getRPData(db)
            role_dict = defaultdict(list)
            for entry in data:
                r_id = entry.role_id  # Extracting role ID
                role_dict[r_id].append(
                    {"module_id": entry.module_id, "permission_id": entry.permission_id}
                )

            if role_id:
                role_id = int(role_id)
                if not role_dict.get(role_id, []):
                    return JSONResponse(
                        content={
                            translate(
                                "message", lang=accept_language
                            ): "Role ID Not Found."
                        },
                        status_code=400,
                    )
                perm_logger.info(f"Returning permissions for role_id: {role_id}")
                return JSONResponse(
                    content={
                        translate(
                            "message", lang=accept_language
                        ): "Role permission fetched.",
                        str(role_id): role_dict.get(role_id, []),
                    },
                    status_code=200,
                )

            perm_logger.info("Returning all role permissions.")
            return JSONResponse(
                content={
                    translate(
                        "message", lang=accept_language
                    ): "Fetched all roles successfully.",
                    "data": role_dict,
                },
                status_code=200,
            )
        except Exception as e:
            perm_logger.error(f"Get Role Permission failed: {str(e)}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def addRolePermission(data, db, accept_language):
        """
        Add a new role permission to the database.
        """
        try:
            perm_logger.info("Adding new role permission.")
            role_id = data.get("role_id")
            module_id = data.get("module_id")
            permission_id = data.get("permission_id")

            if not role_id or not module_id or not permission_id:
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        **translate_pair(
                            "message", "must_fill_all", lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            # Convert inputs to integers
            # try:
            #     role_id = role_id
            #     module_id = module_id
            #     permission_id = permission_id
            # except ValueError:
            #     return JSONResponse(
            #         content={
            #             **translate_pair("success", "false", lang=accept_language),
            #             **translate_pair(
            #                 "message", "invalid_input", lang=accept_language
            #             ),
            #         },
            #         status_code=400,
            #     )

            perm_logger.info(
                f"Received role_id: {role_id}, module_id: {module_id}, permission_id: {permission_id}"
            )

            verificationID = await verifyModuleRolendPermID(
                role_id, module_id, permission_id, db, accept_language
            )
            if verificationID.status_code == 400:
                return verificationID

            existing_role_permission = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == role_id,
                    RolePermission.module_id == module_id,
                    RolePermission.permission_id == permission_id,
                    RolePermission.is_deleted == 0,
                )
                .all()
            )
            if existing_role_permission:
                perm_logger.warning(f"RolePermission creation failed: Duplicate Entry.")

                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["Role Permission", "already_exists"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            dataList = [role_id, module_id, permission_id]
            uploadData = RolePerm_DBConn.addRolePerm(dataList, db, accept_language)
            if uploadData.status_code != 201:
                perm_logger.warning("Role Permission Not Added")
            else:
                perm_logger.info("Role permission added successfully.")
            return uploadData

        except Exception as e:
            perm_logger.error(f"Add Role Permission failed: {e}")  # ✅ Fixed line
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateRolePermission(data, db, accept_language):
        """
        Update an existing role permission in the database.
        """
        perm_logger.info("Updating role permission.")
        try:
            rp_id = data.get("rp_id") if data.get("rp_id") else ""
            role_id = data.get("role_id") if data.get("role_id") else ""
            module_id = data.get("module_id") if data.get("module_id") else ""
            permission_id = (
                data.get("permission_id") if data.get("permission_id") else ""
            )

            perm_logger.info(
                f"Received update request for rp_id: {rp_id}, role_id: {role_id}, module_id: {module_id}, permission_id: {permission_id}"
            )
            if not rp_id:
                perm_logger.warning("Missing Role Permission ID")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["role", "permission", "mandatory"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )
            # if not str(rp_id).isdigit():
            #     return JSONResponse(
            #         content={"message": "Invalid Input", "success": "false"},
            #         status_code=400,
            #     )
            result = Perm_Serv.updateRolePermissionService(
                rp_id, role_id, module_id, permission_id, db, accept_language
            )

            if isinstance(result, JSONResponse):
                perm_logger.warning(
                    "Update failed. No changes detected or invalid role permission ID."
                )
                return result

            recentUpdate, data2update = result
            uploadData = RolePerm_DBConn.updateRolePermissionDB(
                recentUpdate, data2update, rp_id, db, accept_language
            )

            if not uploadData.status_code > 400:
                perm_logger.info("Updated Successfully.")
            return uploadData
        except Exception as e:
            perm_logger.error(f"Update Role Permission failed: {e}")  # ✅ Fixed line
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def deleteRolePermission(rp_id, db, accept_language):
        """
        Delete a role permission from the database.
        """
        try:
            perm_logger.info("Received request to delete role permission.")

            rolePermissionData = RolePerm_DBConn.getRPData(db)
            rolePermission = None  # 💥 FIXED: Declare default
            for i in rolePermissionData:
                if i.id == rp_id:
                    rolePermission = i
                    break

            if rolePermission:
                result = RolePerm_DBConn.deleteRp(rp_id, db)
                if result.status_code == 200:
                    perm_logger.info(
                        f"Role permission with ID {rp_id} deleted successfully."
                    )
                return result
            else:
                return JSONResponse(
                    content={"message": "Role Permission Not found", "success": False},
                    status_code=400,
                )

        except Exception as e:
            perm_logger.error(f"Delete Role Permission failed: {str(e)}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def getSingleUserPermission(email, user_id, db, accept_language):
        """
        Retrieve a single user's permission details using either email or user_id.
        If email is provided but not user_id, fetch user_id from the database.
        """
        perm_logger.info("Received request to fetch single user permission.")

        try:
            # Validate input fields
            if not email and not user_id:
                perm_logger.warning("Missing mandatory fields: email or user_id.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        **translate_pair(
                            "message", "must_fill_all", lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            # Retrieve user_id if only email is provided
            if email and not user_id:
                try:
                    user_id = [
                        i.id
                        for i in user_databaseConnection.getUserTable(db)
                        if i.email == email
                    ][0]
                except IndexError:
                    perm_logger.error(f"User with email '{email}' not found.")
                    return JSONResponse(
                        content={
                            **translate_pair("success", "false", lang=accept_language),
                            translate("message", lang=accept_language): translate_many(
                                ["user", "not_found"], lang=accept_language
                            ),
                        },
                        status_code=400,
                    )

            perm_logger.info(f"Fetching permission details for user_id: {user_id}")

            # Fetch permission details
            result = Perm_Serv.getSingleUserPermission_Serv(
                user_id, db, accept_language
            )
            if isinstance(result, JSONResponse):
                perm_logger.warning("Failed to fetch user permission details.")
                return result

            email_id, role_permission, user_permission = result

            response = {
                "data": {
                    "user id": user_id,
                    "email id": email_id,
                    "role permission": role_permission,
                    "user permission": user_permission,
                }
            }

            perm_logger.info(
                f"Successfully retrieved user permission details for user_id: {user_id}"
            )
            return JSONResponse(content=response, status_code=200)
        except Exception as e:
            perm_logger.error(f"get Single User Permission failed: {e}")
            # perm_logger.error("get Single User Permission failed: ", str(e))
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def getUserPermission(user_id, db, accept_language):
        """
        Retrieve user permissions from the database.
        If 'user_id' is provided, return permissions specific to that user.
        """
        perm_logger.info("Fetching user permissions from the database.")
        try:
            data = UserPerm_DBConn.getUserPData(db)

            user_dict = defaultdict(list)
            for entry in data:
                u_id = entry.user_id  # Extracting user ID
                userPermissionID = entry.id
                user_dict[u_id].append(
                    {
                        "user_id": entry.user_id,
                        "module_id": entry.module_id,
                        "permission_id": entry.permission_id,
                    }
                )

            if user_id:
                user_id = int(user_id)

                if user_dict.get(user_id) is None:
                    perm_logger.warning(f"No permissions found for user_id: {user_id}")
                    return JSONResponse(
                        content={userPermissionID: "No user permissions."}
                    )

                perm_logger.info(f"Returning permissions for user_id: {user_id}")
                return JSONResponse(
                    content={
                        translate(
                            "message", lang=accept_language
                        ): "Fetched user permissions successfully.",
                        str(userPermissionID): user_dict.get(user_id, []),
                    },
                    status_code=200,
                )

            perm_logger.info("Returning all user permissions.")
            return JSONResponse(
                content={
                    translate(
                        "message", lang=accept_language
                    ): "Fetched all users successfully.",
                    "data": user_dict,
                },
                status_code=200,
            )
        except Exception as e:
            perm_logger.error(f"Get User Permission failed: {e}")
            return JSONResponse(
                content={
                    translate("message", lang=accept_language): str(e),
                    "success": False,
                },
                status_code=400,
            )

    @staticmethod
    async def addUserPermission(data, db, accept_language):
        """
        Add a new user permission to the database.
        """
        perm_logger.info("Adding new user permission.")
        try:
            user_id = data.get("user_id")
            module_id = data.get("module_id")
            permission_id = data.get("permission_id")

            if not user_id or not module_id or not permission_id:
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        **translate_pair(
                            "message", "must_fill_all", lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            perm_logger.info(
                f"Received user_id: {user_id}, module_id: {module_id}, permission_id: {permission_id}"
            )

            verificationID = await verifyModuleUserndPermID(
                user_id, module_id, permission_id, db, accept_language
            )
            if verificationID.status_code == 400:
                return verificationID

            existing_user_permission = (
                db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user_id,
                    UserPermission.module_id == module_id,
                    UserPermission.permission_id == permission_id,
                    UserPermission.is_deleted == 0,
                )
                .all()
            )
            if existing_user_permission:
                perm_logger.warning(f"UserPermission creation failed: Duplicate Entry.")

                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["User Permission", "already_exists"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            dataList = [user_id, module_id, permission_id]

            uploadData = UserPerm_DBConn.addUserPerm(dataList, db)
            if not uploadData:
                perm_logger.warning("User permission already exists.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "permission", "already_exists"],
                            lang=accept_language,
                        ),
                    },
                    status_code=400,
                )

            perm_logger.info("User permission added successfully.")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["user", "permission", "added_successfully"],
                        lang=accept_language,
                    ),
                },
                status_code=200,
            )
        except Exception as e:
            perm_logger.error(f"Add User Permission failed: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateUserPermission(data, db, accept_language):
        """
        Update an existing user permission in the database.
        Validates and updates fields only if changes are detected.
        """
        perm_logger.info("Received request to update user permission.")
        try:
            up_id = data.get("up_id") if data.get("up_id") else ""
            user_id = data.get("user_id") if data.get("user_id") else ""
            module_id = data.get("module_id") if data.get("module_id") else ""
            permission_id = (
                data.get("permission_id") if data.get("permission_id") else ""
            )

            if not up_id:
                perm_logger.warning("Missing User Permission ID")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "permission", "mandatory"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            perm_logger.info(
                f"Updating User Permission - up_id: {up_id}, user_id: {user_id}, module_id: {module_id}, permission_id: {permission_id}"
            )

            # Validate and check for changes
            result = Perm_Serv.updateUserPermissionService(
                up_id, user_id, module_id, permission_id, db, accept_language
            )
            if isinstance(result, JSONResponse):
                perm_logger.warning(
                    "Validation failed or user permission does not exist."
                )
                return result
            recentUpdate, data2update = result
            if not recentUpdate and not data2update:
                perm_logger.info("No changes detected in user permission.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate(
                            "message", lang=accept_language
                        ): "Nothing to change or User Permission already exists",
                    },
                    status_code=400,
                )

            # Update user permission in the database
            uploadData = UserPerm_DBConn.updateUserPermissionDB(
                recentUpdate, data2update, up_id, db
            )
            if not uploadData.status_code > 400:
                return uploadData

            # Construct updated data response
            updated_data = {
                recentUpdate[i]: data2update[i] for i in range(len(recentUpdate))
            }
            perm_logger.info(f"User permission updated successfully for up_id: {up_id}")

            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["user", "permission", "added_successfully"],
                        lang=accept_language,
                    ),
                    "updated_fields": updated_data,
                },
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={
                    **translate_pair("success", "false", lang=accept_language),
                    **translate_pair(
                        "message", f"unexpected_error {e}", lang=accept_language
                    ),
                },
                status_code=400,
            )

    @staticmethod
    async def deleteUserPermission(up_id, db, accept_language):
        """
        Delete a user permission from the database.
        """
        perm_logger.info("Received request to delete user permission.")
        try:
            if not up_id:
                perm_logger.warning("User Permission ID is missing in the request.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "permission", "mandatory"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            # Perform deletion operation
            success = UserPerm_DBConn.deleteUP(up_id, db)
            perm_logger.info(f"User permission deleted successfully - up_id: {up_id}")

            if not success:
                perm_logger.warning(
                    f"User permission not found or failed to delete - up_id: {up_id}"
                )
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "permission", "not_found"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["user", "permission", "deleted_successfully"],
                        lang=accept_language,
                    ),
                    "deleted_field": up_id,
                },
                status_code=200,
            )
        except Exception as e:
            perm_logger.error(f"Delete User Permission failed: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def addModule(add_module_data: dict, db, accept_language, current_user):
        """
        Add a new module to the system.
        Uses the authenticated user's email to track who created the module.
        """
        try:
            perm_logger.info("Received request to add a new module.")
            # Extract request parameters
            name = add_module_data["name"]
            createdByEmail = current_user["user_id"]

            if not name:
                return JSONResponse(
                    content={
                        translate(
                            "message", lang=accept_language
                        ): "Module name is required."
                    },
                    status_code=400,
                )
            existing_module = (
                db.query(Module)
                .filter(Module.name == name, Module.is_deleted == 0)
                .all()
            )
            if existing_module:
                perm_logger.warning(
                    f"Module creation failed: Module '{name}' already exists."
                )

                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["module", "already_exists"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            perm_logger.info(f"Adding new module: {name}, created by: {createdByEmail}")

            # Insert new module into database
            uploadData = Module_DBConn.addModDB(name, createdByEmail, db)
            if not uploadData.status_code > 400:
                perm_logger.warning(f"Module '{name}' already exists.")
            else:
                perm_logger.info(f"Module '{name}' added successfully.")
            return uploadData
        except Exception as e:
            perm_logger.error(f"Add Module failed: {e}")
            return JSONResponse(
                content={
                    **translate_pair("success", "false", lang=accept_language),
                    translate("message", lang=accept_language): str(e),
                },
                status_code=400,
            )

    @staticmethod
    async def getModule(module_id, db, accept_language):
        """
        Fetch modules:
        - If module_id is given, return that module.
        - If not, return all modules.
        """
        perm_logger.info("Received request to fetch module(s).")

        try:
            all_modules = Module_DBConn.getModuleData(db)

            if module_id:
                module_id = int(module_id)
                all_modules = [m for m in all_modules if m.id == module_id]
                perm_logger.info(f"Fetching module with ID: {module_id}")
            else:
                perm_logger.info("Fetching all active modules.")

            if not all_modules:
                perm_logger.warning(f"No module found for module_id: {module_id}")
                return JSONResponse(
                    content={
                        **translate_pair("success", "true", lang=accept_language),
                        **translate_pair(
                            "message", "no_data_found", lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            response = {
                translate("message", lang=accept_language): translate_many(
                    ["modules", "fetched"], lang=accept_language
                ),
                **translate_pair("success", "true", lang=accept_language),
                "data": [
                    {
                        "module_id": m.id,
                        "name": m.name,
                        "created_by": m.created_by,
                    }
                    for m in all_modules
                ],
            }

            perm_logger.info(f"Successfully retrieved {len(all_modules)} module(s).")
            return JSONResponse(content=response, status_code=200)

        except Exception as e:
            perm_logger.error(f"Get Module failed: {str(e)}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateModule(data, db, accept_language, current_user):
        """
        Update an existing module.
        - Requires module_id and modified_by.
        - Returns updated fields upon success.
        """
        try:
            perm_logger.info("Received request to update module.")

            # Extract and validate module_id
            module_id_raw = data.get("module_id")
            if not module_id_raw:
                perm_logger.warning("Module ID is missing.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["Module ID", "mandatory"],
                            lang=accept_language,
                        ),
                    },
                    status_code=400,
                )

            try:
                module_id = int(module_id_raw)
            except ValueError:
                perm_logger.warning("Invalid Module ID type.")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Invalid module id. Module ID should be Integer.",
                    },
                    status_code=400,
                )

            name = data.get("name") if data.get("name") else None
            modified_by = current_user["user_id"]

            # Update module via service
            updated_data = Module_Serv.updateModule_Serv(
                module_id, name, modified_by, db, accept_language
            )

            if isinstance(updated_data, JSONResponse):
                perm_logger.error(
                    f"Failed to update module {module_id}. Reason: {updated_data}"
                )
                return updated_data

            perm_logger.info(f"Module {module_id} updated successfully.")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["Modules", "updated_successfully"], lang=accept_language
                    ),
                    "updated_fields": updated_data,
                },
                status_code=201,
            )

        except Exception as e:
            perm_logger.error(f"Update Module failed: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": str(e),
                    translate(
                        "message", lang=accept_language
                    ): "Module update failed. Cannot add duplicate module.",
                },
            )

    @staticmethod
    async def deleteModule(module_id, db, accept_language):
        """
        Delete a module by module_id.
        """
        perm_logger.info("Received request to delete module.")
        try:
            # Call service layer to delete module
            deleteStatus = Module_Serv.deleteModule_Serv(module_id, db, accept_language)
            if isinstance(deleteStatus, JSONResponse):
                return deleteStatus

            perm_logger.info(f"Module {module_id} deleted successfully.")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["module", "deleted_successfully"], lang=accept_language
                    ),
                    "deleted_field": module_id,
                },
                status_code=200,
            )
        except Exception as e:
            perm_logger.error(f"Delete Module failed: {e}")
            return JSONResponse(
                content={
                    "success": False,
                    translate("message", lang=accept_language): str(e),
                },
                status_code=400,
            )

    @staticmethod
    async def addPermission(add_perm_data: dict, db, accept_language):
        """
        Add a new permission.
        - Requires 'name' in request form.
        """
        perm_logger.info("Received request to add permission.")
        try:
            name = add_perm_data["name"]
            if not name:
                perm_logger.warning("Permission name is mandatory.")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["name", "mandatory"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )

            created_by = add_perm_data["current user"]["user_id"]

            existing_permission = (
                db.query(Permission)
                .filter(Permission.name == name, Permission.is_deleted == 0)
                .all()
            )
            if existing_permission:
                perm_logger.warning(
                    f"existing_permission creation failed: existing_permission '{name}' already exists."
                )

                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["permission", "already_exists"],
                            lang=accept_language,
                        ),
                    },
                    status_code=400,
                )

            # Call service layer to add permission
            result = Perm_Serv.addPermission_Serv(name, created_by, db, accept_language)

            perm_logger.info(f"Permission '{name}' added successfully.")
            return result
        except Exception as e:
            perm_logger.error("Add Permission failed: ", str(e))
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def getPermission(permission_id, db, accept_language):
        """
        Retrieve permission details.
        - If permission_id is provided, return specific permission details.
        - If no permission_id is provided, return all permissions.
        """
        perm_logger.info("Received request to fetch permission details.")
        try:
            if permission_id and not str(permission_id).isdigit():
                return JSONResponse(
                    content={
                        translate("message", lang=accept_language): translate_many(
                            ["digits_only", "permission", "id"], lang=accept_language
                        )
                    },
                    status_code=400,
                )
            # Call service layer to fetch permissions
            response = await Perm_Serv.getPermission_Serv(
                permission_id, db, accept_language
            )

            perm_logger.info(
                f"Fetched permission details for permission_id: {permission_id}"
                if permission_id
                else "Fetched all permissions."
            )
            return response
        except Exception as e:
            perm_logger.error(f"Get Permission failed: {e}")
            return JSONResponse(
                content={
                    "success": False,
                    translate("message", lang=accept_language): str(e),
                },
                status_code=400,
            )

    @staticmethod
    async def updatePermission(data, db, accept_language, current_user):
        """
        Update an existing permission.
        - Requires valid permission_id.
        - Returns updated fields upon success.
        """
        perm_logger.info("Received request to update permission.")

        try:
            # Extract and validate permission_id
            permission_id_raw = data.get("permission_id")
            if not permission_id_raw:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Permission ID mandatory",
                    },
                    status_code=400,
                )

            try:
                permission_id = int(permission_id_raw)
            except (TypeError, ValueError):
                perm_logger.warning(f"Invalid permission_id: {permission_id_raw}")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Permission ID must be Integer",
                    },
                    status_code=400,
                )

            name = data.get("name") or None
            modified_by = current_user["user_id"]

            # Call service layer
            updated_data = Perm_Serv.updatePerm_Serv(
                permission_id, name, modified_by, db, accept_language
            )

            if isinstance(updated_data, JSONResponse):
                perm_logger.error(
                    f"Failed to update permission {permission_id}. Reason: {updated_data.body}"
                )
                return updated_data

            perm_logger.info(f"Permission {permission_id} updated successfully.")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["permission", "updated_successfully"], lang=accept_language
                    ),
                    "updated_fields": updated_data,
                },
                status_code=200,
            )

        except Exception as e:
            perm_logger.error(f"Update Permission failed: {str(e)}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def deletePermission(permission_id, db, accept_language):
        """
        Delete a permission by permission_id.
        """
        perm_logger.info("Received request to delete permission.")
        try:
            # Call service layer to delete permission
            result = await Perm_Serv.deletePermission_Serv(
                permission_id, db, accept_language
            )
            if result.status_code == 400:
                perm_logger.error(
                    f"Failed to delete permission {permission_id}. Reason: {result}"
                )
                return result
            else:
                perm_logger.info(f"Permission {permission_id} deleted successfully.")
                return result
        except Exception as e:
            perm_logger.error(f"Delete Permission failed: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )


# FROM ADD MODULE
# Retrieve user_id from email
# users_details = user_databaseConnection.getUserTable(db)
# try:
#     createdByEmail = [
#         data.id for data in users_details if data.email == createdByEmail
#     ][0]
# except IndexError:
#     perm_logger.error(
#         f"Creator email '{createdByEmail}' not found in user database."
#     )
#     return JSONResponse(
#         content={
#             **translate_pair("success", "false", lang=accept_language),
#             translate("message", lang=accept_language): "User not found",
#         },
#         status_code=400,
#     )
