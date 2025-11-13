from dao.v1.perm_dao import RolePerm_DBConn, UserPerm_DBConn, Permissions_DBConn
from dao.v1.user_dao import user_databaseConnection
from dao.v1.module_dao import Module_DBConn
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
import logging
from dao.v1.perm_dao import Permissions_DBConn

# Configure rotating file handler
import os
import logging
from logging.handlers import RotatingFileHandler

# Detect environment
is_render = os.getenv("RENDER", "false").lower() == "true"

# Create logger
perm_logger = logging.getLogger("perm_services")
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
        f"{log_dir}/perm_services.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )

log_handler.setFormatter(formatter)
perm_logger.addHandler(log_handler)


class Perm_Serv:

    def updateRolePermissionService(rp_id, role_id, module_id, permission_id, db):
        """Update role permission details based on provided IDs."""

        perm_logger.info("updateRolePermissionService called with rp_id: %s", rp_id)

        # Fetch existing role permission data
        oldRolePermission = next(
            (i for i in RolePerm_DBConn.getRPData(db) if i.id == rp_id), None
        )

        if not oldRolePermission:
            perm_logger.error("Role permission ID %s not found.", rp_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Role Permission ID not available.",
                },
                status_code=400,
            )

        # Field mappings for comparison
        fields_to_check = {
            "role_id": role_id,
            "module_id": module_id,
            "permission_id": permission_id,
        }

        recentUpdate, data2update = [], []
        for field, new_value in fields_to_check.items():
            if new_value is not None and getattr(oldRolePermission, field) != new_value:
                recentUpdate.append(field)
                data2update.append(new_value)

        perm_logger.info(
            "Role Permission ID %s updated fields: %s", rp_id, recentUpdate
        )
        return recentUpdate, data2update

    def updateUserPermissionService(up_id, user_id, module_id, permission_id, db):
        """Update user permission details based on provided IDs."""

        perm_logger.info("updateUserPermissionService called with up_id: %s", up_id)

        # Fetch user permission data
        all_permissions = UserPerm_DBConn.getUserPData(db)
        data = next((i for i in all_permissions if i.id == up_id), None)

        if data is None:
            perm_logger.error(f"User permission ID %s not found {up_id}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "User Permission ID not available",
                },
                status_code=400,
            )

        # Validate user_id existence
        valid_user_ids = {i.id for i in user_databaseConnection.getUserTable(db)}
        if user_id not in valid_user_ids:
            perm_logger.error(f"User ID %s not found {user_id}")
            return JSONResponse(
                content={"success": False, "message": "User ID not available"},
                status_code=400,
            )

        recentUpdate, data2update = [], []

        # Field comparison
        fields_to_check = {
            "user_id": user_id,
            "module_id": module_id,
            "permission_id": permission_id,
        }

        for field, new_value in fields_to_check.items():
            if new_value is not None and getattr(data, field) != new_value:
                recentUpdate.append(field)
                data2update.append(new_value)

        perm_logger.info(
            "User Permission ID %s updated fields: %s", up_id, recentUpdate
        )
        return recentUpdate, data2update

    def getSingleUserPermission_Serv(user_id, db):
        """Retrieve permissions associated with a single user."""

        perm_logger.info(
            f"getSingleUserPermission_Serv called with user_id: %s{user_id}"
        )

        # Fetch permissions for the user
        data = UserPerm_DBConn.getPermissionsOfUser(user_id, db)

        if not data:
            perm_logger.warning(f"No permission data found for user_id: {user_id}")
            return JSONResponse(
                content={"success": False, "message": "Permission not found."},
                status_code=400,
            )

        email_id = data[0][0]  # Extract email ID
        role_permission, user_permission = {}, {}
        # Processing role and user permissions
        for entry in data:
            role_id, permission_id, user_id, user_perm = (
                entry[2],
                entry[3],
                entry[4],
                entry[5],
            )

            if role_id and permission_id:
                role_permission.setdefault(str(role_id), []).append(permission_id)

            if user_id and user_perm:
                user_permission.setdefault(str(user_id), []).append(user_perm)

        # Removing duplicates and sorting permissions
        role_permission = {k: sorted(set(v)) for k, v in role_permission.items()}
        user_permission = {k: sorted(set(v)) for k, v in user_permission.items()}

        perm_logger.info(
            "User permissions retrieved successfully for user_id: %s", user_id
        )
        return (email_id, role_permission, user_permission)

    def addPermission_Serv(name, created_by, db):
        """Add a new permission if it doesn't already exist."""

        # Attempt to add permission to the database
        uploadData = Permissions_DBConn.addPermissionDB(name, created_by, db)
        if uploadData.status_code < 400:
            perm_logger.info("Permission '%s' added successfully.", name)
        return uploadData

    async def getPermission_Serv(permission_id, db):
        """Retrieve permission details based on permission_id."""

        perm_logger.info(
            "getPermission_Serv called with permission_id: %s", permission_id
        )

        # If no specific permission_id is given, return all permissions
        if not permission_id:
            data = [i for i in Permissions_DBConn.getPermissionData(db)]

            perm_logger.info("Returning all permissions.")
            return JSONResponse(
                content={
                    "message": "Data fetched successfully.",
                    "success": True,
                    "data": [
                        {
                            "permission_id": i.id,
                            "name": i.name,
                            "created_by": i.created_by,
                        }
                        for i in data
                    ],
                },
                status_code=200,
            )

        # Retrieve specific permission by ID
        data = [
            i
            for i in Permissions_DBConn.getPermissionData(db)
            if i.id == int(permission_id)
        ]

        if not data:
            perm_logger.error("Permission ID %s not found", permission_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission not found.",
                },
                status_code=400,
            )

        perm_logger.info(
            "Permission details retrieved for permission_id: %s", permission_id
        )
        return JSONResponse(
            content={
                "message": "Data fetched successfully.",
                "success": True,
                "data": [
                    {"permission_id": i.id, "name": i.name, "created_by": i.created_by}
                    for i in data
                ],
            },
            status_code=200,
        )

    def updatePerm_Serv(permission_id, name, modified_by, db):
        # Update an existing permission.

        perm_logger.info("updatePerm_Serv called with permission_id: %s", permission_id)

        if not permission_id or not modified_by:
            perm_logger.error("Permission ID and Modified By are mandatory.")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission ID and Modified By are mandatory.",
                },
                status_code=400,
            )

        permission_ids = [i.id for i in Permissions_DBConn.getPermissionData(db)]
        if permission_id not in permission_ids:
            perm_logger.warning("Permission ID %s not available.", permission_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission ID not available.",
                },
                status_code=400,
            )

        permission_data = [
            i for i in Permissions_DBConn.getPermissionData(db) if i.id == permission_id
        ]
        if not permission_data:
            perm_logger.error("Permission ID %s not found.", permission_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission not found.",
                },
                status_code=400,
            )

        permission_data = permission_data[0]
        recentUpdate, data2update = [], []

        if name and name != permission_data.name:
            recentUpdate.append("name")
            data2update.append(name)

        if modified_by and modified_by != permission_data.modified_by:
            recentUpdate.append("modified_by")
            data2update.append(modified_by)

        if not recentUpdate:
            perm_logger.warning(
                "No changes detected for Permission ID %s.", permission_id
            )
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Nothing to change or permission already exists.",
                },
                status_code=400,
            )

        update_status = Permissions_DBConn.updatePermissionDB(
            recentUpdate, data2update, permission_id, db
        )

        if update_status.status_code < 400:
            perm_logger.info("Permission ID %s updated successfully.", permission_id)

            updated_data = {
                recentUpdate[i]: data2update[i] for i in range(len(recentUpdate))
            }
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Permission updated successfully.",
                    "updated_fields": updated_data,
                },
                status_code=200,
            )

        # Now handle duplicate error case
        response_json = update_status.body.decode()  # Extract JSON from JSONResponse
        if "Duplicate entry" in response_json:
            perm_logger.error(
                "Permission update failed for permission_id %s. Duplicate entry.",
                permission_id,
            )
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission update failed. Cannot add duplicate permission.",
                },
                status_code=400,
            )

        # If it’s some other error, just return the existing response
        return update_status

    async def deletePermission_Serv(permission_id, db):
        # Delete a permission based on permission_id.

        perm_logger.info(
            "deletePermission_Serv called with permission_id: %s", permission_id
        )

        permission_ids = [i.id for i in Permissions_DBConn.getPermissionData(db)]
        if permission_id not in permission_ids:
            perm_logger.warning("Permission ID %s not found.", permission_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission not found.",
                },
                status_code=400,
            )

        delete_status = Permissions_DBConn.deletePermissionDB(permission_id, db)

        if isinstance(delete_status, str):
            perm_logger.error(
                "Permission deletion failed for permission_id %s. It might be in use.",
                permission_id,
            )
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Permission deletion failed. Maybe the permission is in use.",
                },
                status_code=400,
            )

        perm_logger.info("Permission ID %s deleted successfully.", permission_id)
        return JSONResponse(
            content={
                "success": True,
                "message": "Permission deleted successfully.",
                "deleted_field": permission_id,
            },
            status_code=200,
        )


class Module_Serv:
    @staticmethod
    def updateModule_Serv(module_id, name, modified_by, db):
        """Update module details."""

        # Log that the update function has been called
        perm_logger.info("updateModule_Serv called with module_id: %s", module_id)

        # Fetch all module IDs from the database
        module_ids = [i.id for i in Module_DBConn.getModuleData(db)]

        # Check if the provided module_id exists
        if module_id not in module_ids:
            perm_logger.warning("Module ID %s not available.", module_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Module ID not available.",
                },
                status_code=400,
            )

        # Retrieve the module data for the given module_id
        module_data = [i for i in Module_DBConn.getModuleData(db) if i.id == module_id]

        # If no data is found, log an error and return a response
        if not module_data:
            perm_logger.error("Module ID %s not found.", module_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Module not found.",
                },
                status_code=400,
            )

        module_data = module_data[0]  # Extract the first element since it is a list
        recentUpdate, data2update = [], []  # Lists to store fields that need updating

        # Check if the name is provided and different from the existing value
        if name and name != module_data.name:
            recentUpdate.append("name")
            data2update.append(name)

        # Check if modified_by is provided and different from the existing value
        if modified_by and modified_by != module_data.modified_by:
            recentUpdate.append("modified_by")
            data2update.append(modified_by)

        # Update the database with the new values
        update_status = Module_DBConn.updateModuleDB(
            recentUpdate, data2update, module_id, db
        )

        # If the update fails due to a duplicate entry, log an error and return a response
        if update_status.status_code < 400:
            # Create a dictionary of updated fields
            updated_data = {
                recentUpdate[i]: data2update[i] for i in range(len(recentUpdate))
            }
            # Log a successful update message
            perm_logger.info("Module ID %s updated successfully.", module_id)
            return updated_data
        response = update_status.body.decode()
        if "Duplicate entry" in response:
            perm_logger.error(
                "Module update failed for module_id %s. Duplicate entry.", module_id
            )
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Module update failed. Cannot add duplicate module.",
                },
                status_code=400,
            )
        else:
            return update_status

    @staticmethod
    def deleteModule_Serv(module_id, db):
        """Delete a module based on module_id."""

        # Log that the delete function has been called
        perm_logger.info("deleteModule_Serv called with module_id: %s", module_id)

        # Fetch all module IDs from the database
        module_ids = [i.id for i in Module_DBConn.getModuleData(db)]

        # Check if module_id exists in the database
        if module_id not in module_ids:
            perm_logger.warning("Module ID %s not found.", module_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Module not found.",
                },
                status_code=400,
            )

        # Attempt to delete the module from the database
        delete_status = Module_DBConn.deleteModuleDB(module_id, db)

        # If deletion is successful, log success and return True
        if delete_status:
            perm_logger.info("Module ID %s deleted successfully.", module_id)
            return True
        else:
            # If deletion fails, log an error and return a response
            perm_logger.error("Module deletion failed for module_id %s.", module_id)
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Something went wrong.",
                },
                status_code=400,
            )
