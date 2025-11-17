from services.v1.user_services import user_services
from dao.v1.user_dao import user_databaseConnection
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
import logging


import os


# Detect if running on Render
is_render = os.getenv("RENDER", "false").lower() == "true"

# Create the logger
user_logger = logging.getLogger("user_logger")
user_logger.setLevel(logging.INFO)

# Formatter for all logs
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

if is_render:
    # ✅ Render environment → logs shown in Render dashboard
    log_handler = logging.StreamHandler()
else:
    # ✅ Local environment → logs saved to file
    log_dir = "logs/v1"
    os.makedirs(log_dir, exist_ok=True)  # this prevents FileNotFoundError

    log_handler = RotatingFileHandler(
        f"{log_dir}/user_controller.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )

log_handler.setFormatter(formatter)
user_logger.addHandler(log_handler)


class UserController:
    @staticmethod
    async def getAllUser(userID, db):
        """Retrieves details of all users or a specific user by ID."""
        try:
            user_logger.info(f"getAllUser called with user ID: {userID}")

            # Call service layer to get users
            result = await user_services.getAlluser_serv(userID, db)

            return result
        except Exception as e:
            user_logger.error(f"error: {e}")
            return JSONResponse(
                content={"message": str(e)},
                status_code=400,
            )

    @staticmethod
    async def updateUser(data, db, current_user):
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
            result = await user_services.updateUser_serv(dataList, db)
            user_logger.info("updateUser successful")
            return result
        except Exception as e:
            user_logger.error(f"updateUser failed: {str(e)}")
            return JSONResponse(
                content={"message": str(e)},
                status_code=400,
            )

    @staticmethod
    async def deleteUser(id, db):
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
                        "success": True,
                        "message": "User deleted successfully.",
                    },
                    status_code=200,
                )
            else:
                user_logger.error("User not deleted")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "User deletion failed.",
                    },
                    status_code=400,
                )
        except Exception as e:
            user_logger.error(f"deleteUser failed: {e}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": str(e),
                },
                status_code=400,
            )

    # @staticmethod
    # def deleteAllUser():
    #     #! CURRENTLY NOT AVAILABLE
    #     return JSONResponse(
    #         content={"status": True, "message": "Deleted Successfully"},
    #         status_code=200,
    #     )
