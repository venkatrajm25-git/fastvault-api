from utils.v1.lang_utils import translate, translate_many, translate_pair
from dao.v1.module_dao import Module_DBConn
from dao.v1.user_dao import user_databaseConnection
from dao.v1.perm_dao import Permissions_DBConn
from fastapi.responses import JSONResponse
from dao.v1.role_dao import Role_DBConn


async def verifyModuleRolendPermID(
    role_id, module_id, permission_id, db, accept_language
):
    # Fetch existing Role IDs from the database
    data = [i.id for i in Role_DBConn.getRoleData(db)]
    if role_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["role", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    # Fetch existing Module IDs from the database
    data = [i.id for i in Module_DBConn.getModuleData(db)]
    if module_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["module", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    # Fetch existing Permission IDs from the database
    data = [i.id for i in Permissions_DBConn.getPermissionData(db)]
    if permission_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["permission", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    return JSONResponse(
        content={
            **translate_pair("status", "true", lang=accept_language),
            translate(
                "message", lang=accept_language
            ): "Module Role and Permission ID Verified",
        },
        status_code=201,
    )  # Return True if verification is successful


async def verifyModuleUserndPermID(
    user_id, module_id, permission_id, db, accept_language
):
    # Fetch existing User IDs from the database
    data = [i.id for i in user_databaseConnection.getUserTable(db)]
    if user_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["user", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    # Fetch existing Module IDs from the database
    data = [i.id for i in Module_DBConn.getModuleData(db)]
    if module_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["module", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    # Fetch existing Permission IDs from the database
    data = [i.id for i in Permissions_DBConn.getPermissionData(db)]
    if permission_id not in data:
        return JSONResponse(
            content={
                **translate_pair("status", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["permission", "id", "not_available"], lang=accept_language
                ),
            },
            status_code=400,
        )

    return JSONResponse(
        content={
            **translate_pair("success", "true", lang=accept_language),
            translate(
                "message", lang=accept_language
            ): "Module User and Permission ID Verified",
        },
        status_code=200,
    )  # Return True if verification is successful
