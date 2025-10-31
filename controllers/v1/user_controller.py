from services.v1.user_services import user_services
from utils.v1.lang_utils import translate, translate_many, translate_pair
from dao.v1.user_dao import user_databaseConnection
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
import logging


log_handler = RotatingFileHandler(
    "logs/v1/user_controller.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

user_logger = logging.getLogger("user_logger")
user_logger.setLevel(logging.INFO)
user_logger.addHandler(log_handler)


class UserController:
    @staticmethod
    async def getAllUser(userID, db, accept_language):
        """Retrieves details of all users or a specific user by ID."""
        try:
            user_logger.info(f"getAllUser called with user ID: {userID}")

            # Call service layer to get users
            result = await user_services.getAlluser_serv(userID, db, accept_language)

            return result
        except Exception as e:
            user_logger.error(f"error: {e}")
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateUser(data, db, accept_language, current_user):
        """Updates user details such as username, status, and role."""
        try:
            user_logger.info(f"updateUser called with data: {data}")
            id = data.id
            username = data.username
            status = data.status
            role = data.role
            modifiedby = current_user["user_id"]  # Get modifier info

            dataList = [id, username, status, role, modifiedby]

            # Call service layer to update user
            result = await user_services.updateUser_serv(dataList, db, accept_language)
            # if result :
            #     return result, status_code
            user_logger.info("updateUser successful")
            return result
        except Exception as e:
            user_logger.error("updateUser failed: ", str(e))
            return JSONResponse(
                content={translate("message", lang=accept_language): str(e)},
                status_code=400,
            )

    @staticmethod
    async def deleteUser(id, db, accept_language):
        """Deletes a specific user from the system."""
        try:
            user_logger.info(f"deleteUser called with user ID: {id}")

            success = user_databaseConnection.deleteUserDB(
                id, db
            )  # Perform delete operation

            if success:
                user_logger.info("User deleted successfully: %s", id)
                return JSONResponse(
                    content={
                        **translate_pair("success", "true", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "deleted_successfully"], lang=accept_language
                        ),
                    },
                    status_code=200,
                )
            else:
                user_logger.error("User not deleted")
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["user", "deletion_failed"], lang=accept_language
                        ),
                    },
                    status_code=400,
                )
        except Exception as e:
            user_logger.error(f"deleteUser failed: {e}")
            return JSONResponse(
                content={
                    "success": False,
                    translate("message", lang=accept_language): str(e),
                },
                status_code=400,
            )

    # @staticmethod
    # def deleteAllUser():
    #     #! CURRENTLY NOT AVAILABLE
    #     # # user_logger.info("deleteAllUser called")
    #     # from database.db import getDBConnection
    #     # with getDBConnection() as (db,cursor):
    #     # query = "Delete from users"
    #     # cursor.execute(query)
    #     # db.commit()
    #     # # user_logger.info("All users deleted successfully")
    #     return JSONResponse(
    #         content={"status": True, "message": "Deleted Successfully"},
    #         status_code=200,
    #     )
