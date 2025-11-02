from dao.v1.module_dao import Module_DBConn
from dao.v1.user_dao import user_databaseConnection
from dao.v1.perm_dao import Permissions_DBConn
from fastapi.responses import JSONResponse
from dao.v1.role_dao import Role_DBConn


async def verifyModuleRolendPermID(role_id, module_id, permission_id, db):
    # Fetch existing Role IDs from the database
    data = [i.id for i in Role_DBConn.getRoleData(db)]
    if role_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "Role ID not available",
            },
            status_code=400,
        )

    # Fetch existing Module IDs from the database
    data = [i.id for i in Module_DBConn.getModuleData(db)]
    if module_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "Module ID not available",
            },
            status_code=400,
        )

    # Fetch existing Permission IDs from the database
    data = [i.id for i in Permissions_DBConn.getPermissionData(db)]
    if permission_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "Permission ID not available",
            },
            status_code=400,
        )

    return JSONResponse(
        content={
            "status": True,
            "message": "Module, Role, and Permission ID verified successfully",
        },
        status_code=201,
    )  # Return True if verification is successful


async def verifyModuleUserndPermID(user_id, module_id, permission_id, db):
    # Fetch existing User IDs from the database
    data = [i.id for i in user_databaseConnection.getUserTable(db)]
    if user_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "User ID not available",
            },
            status_code=400,
        )

    # Fetch existing Module IDs from the database
    data = [i.id for i in Module_DBConn.getModuleData(db)]
    if module_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "Module ID not available",
            },
            status_code=400,
        )

    # Fetch existing Permission IDs from the database
    data = [i.id for i in Permissions_DBConn.getPermissionData(db)]
    if permission_id not in data:
        return JSONResponse(
            content={
                "status": False,
                "message": "Permission ID not available",
            },
            status_code=400,
        )

    return JSONResponse(
        content={
            "success": True,
            "message": "Module, User, and Permission ID verified successfully",
        },
        status_code=200,
    )  # Return True if verification is successful
