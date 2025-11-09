from fastapi import Request
from fastapi.responses import JSONResponse
from model.v1.user_model import User
from services.v1.auth_services import AuthServices
from sqlalchemy.orm import Session
from utils.v1.auth_utils import hash_password, verifyResetPassToken
from dao.v1.user_dao import user_databaseConnection
import logging
from utils.v1.utility import generate_reset_token, sendResetLink

# from utils.v1.utility import sendResetLink
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    "logs/v1/auth_controller.log", maxBytes=5 * 1024 * 1024, backupCount=5
)  # 5MB max per file, keeps 5 backups
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

# Get logger and attach handler
auth_logger = logging.getLogger("auth_logger")
auth_logger.setLevel(logging.INFO)
auth_logger.addHandler(log_handler)


class AuthController:

    @staticmethod
    async def register_controller(data, db):
        return await AuthServices.register_serv(data, db)

    @staticmethod
    async def login_controller(data, db):
        return await AuthServices.login_serv(data, db)

    @staticmethod
    def forgetPassword(email, request: Request, background_task, db):
        try:
            receiverEmail = email
            if not receiverEmail:
                return JSONResponse(
                    content={"success": False, "message": "Enter your email"},
                    status_code=400,
                )

            data = user_databaseConnection.getUserTable(db)

            emailList = [i.email for i in data]

            if receiverEmail not in emailList:
                return JSONResponse(
                    content={"success": False, "message": "Email not registered."},
                    status_code=400,
                )

            for i in data:
                if i.email == receiverEmail:
                    user_id = i.id

            raw_token, hashed_token, expires_at = generate_reset_token()

            dataList = [user_id, hashed_token, expires_at]
            saveResetToken = user_databaseConnection.addResetPasswordToken(dataList, db)

            success = sendResetLink(receiverEmail, background_task, db, raw_token)
            auth_logger.info(
                f"email: {receiverEmail} - Forget Password - Mail will be sent."
            )
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Email Sent successfully",
                },
                status_code=200,
            )
        except Exception as e:
            auth_logger.error(f"error: {e}")
            return JSONResponse(content={"message": str(e)}, status_code=400)

    @staticmethod
    async def resetPasswordSubmit(data, db: Session):
        try:
            token = data.token
            password = data.newPassword
            confirm_password = data.confirmPassword

            # Check if passwords match
            if password != confirm_password:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Passwords not matched. Try again.",
                    },
                    status_code=400,
                )

            token_row = await verifyResetPassToken(token, db)

            # Hash new password
            hashed_pwd = hash_password(password)

            # Encode password and generate salt for hashing

            user = db.query(User).filter(User.id == token_row.user_id).first()

            user.pwd = hashed_pwd
            token_row.used = True
            db.commit()

            return JSONResponse(
                content={"success": True, "message": "Password changed successfully."}
            )

        except Exception as e:
            auth_logger.error(f"error: {e}")
            return JSONResponse(
                content={"message": str(e)},
                status_code=400,
            )
