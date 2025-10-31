from utils.v1.lang_utils import translate, translate_many, translate_pair
from dao.v1.user_dao import user_databaseConnection
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

# from helpers.v1.helpers import verifyID

log_handler = RotatingFileHandler(
    "logs/v1/user_services.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

logger = logging.getLogger("user_services")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


class user_services:
    @staticmethod
    async def getAlluser_serv(userID, db: Session, accept_language):
        """
        Retrieve all users or a specific user by userID.
        """
        logger.info("Fetching user(s) data.")  # Logging the operation
        users = []  # Initializing an empty list to store user data

        dbData = user_databaseConnection.getUserTable(
            db
        )  # Fetching all user data from the database

        if isinstance(dbData, dict) and dbData.get("success") is False:
            return JSONResponse(content=dbData, status_code=400)

        if not userID:
            users = [
                {
                    "id": row.id,
                    "email": row.email,
                    "username": row.username,
                    "status": row.status,
                    "role": row.role,
                    "created_by": row.created_by,
                    "modified_by": row.modified_by,
                    "created_at": row.created_at.isoformat(),
                    "modified_at": row.modified_at.isoformat(),
                }
                for row in dbData
            ]
            logger.info("Returning all users data.")
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    "users": users,
                },
                status_code=200,
            )

        # Verify if the provided userID is valid
        # verification = await verifyID(userID, db, accept_language)
        # if verification.status_code == 400:
        #     logger.warning(f"User verification failed for ID: {userID}")
        #     return verification

        # Fetch user data for the provided userID
        data = [row for row in dbData if row.id == userID]
        users = [
            {
                "id": row.id,
                "email": row.email,
                "username": row.username,
                "status": row.status,
                "role": row.role,
                "created_by": row.created_by,
                "modified_by": row.modified_by,
                "created_at": row.created_at.isoformat(),
                "modified_at": row.modified_at.isoformat(),
            }
            for row in data
        ]
        logger.info(f"Returning user data for userID: {userID}")
        if users:
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("user", lang=accept_language): users,
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={
                    **translate_pair("success", "false", lang=accept_language),
                    translate("user", lang=accept_language): translate_many(
                        ["user", "id", "not_found"], lang=accept_language
                    ),
                },
                status_code=400,
            )

    @staticmethod
    async def updateUser_serv(dataList, db, accept_language):
        """
        Update user details.
        """
        id, username, status, role, modifiedby = dataList
        logger.info(f"Attempting to update user: {id}")

        # Fetch user by ID
        data = next(
            (row for row in user_databaseConnection.getUserTable(db) if row.id == id),
            None,
        )
        if not data:
            logger.warning(f"No user found with ID: {id}")
            return JSONResponse(
                content={
                    "success": False,
                    translate("message", lang=accept_language): translate_many(
                        ["user", "not_found"], lang=accept_language
                    ),
                },
                status_code=400,
            )

        fields_to_check = {
            "username": username,
            "status": status,
            "role": role,
            # "modified_by": modifiedby  # Uncomment if modified_by needs update
        }

        updateUser, dataList = [], []
        for field, new_value in fields_to_check.items():
            old_value = getattr(data, field, None)
            if new_value is not None and new_value != old_value:
                updateUser.append(field)
                dataList.append(new_value)

        success = user_databaseConnection.updateUser(id, updateUser, dataList, db)
        if success:
            logger.info(f"User {id} updated successfully.")
            updated_data = {
                "username": username if "username" in updateUser else data.username,
                "status": status if "status" in updateUser else data.status,
                "role": role if "role" in updateUser else data.role,
                "modified_by": (
                    modifiedby if "modified_by" in updateUser else data.modified_by
                ),
            }
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["user", "updated_successfully"], lang=accept_language
                    ),
                    "updated": [updated_data],
                },
                status_code=201,
            )

        return JSONResponse(
            content={
                **translate_pair("success", "false", lang=accept_language),
                translate("message", lang=accept_language): translate_many(
                    ["user", "update_failed"], lang=accept_language
                ),
            },
            status_code=400,
        )
