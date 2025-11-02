from dao.v1.auth_dao import AuthDAO
from fastapi.responses import JSONResponse
from utils.v1.auth_utils import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from utils.v1.token_generation import create_access_token, create_refresh_token


class AuthServices:
    @staticmethod
    async def register_serv(data, db):
        try:
            email = data.email
            password = hash_password(data.password)  # hash password
            username = data.username
            status = data.status
            role = data.role
            created_by = 1

            user_details = [email, password, username, status, role, created_by]
            user_id = AuthDAO.register_user_dao(user_details, db)

            return JSONResponse(
                content={
                    "success": True,
                    "message": "User Created Successfully.",
                    "user_id": user_id,
                },
                status_code=201,
            )
        except IntegrityError as duplicateError:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "User Email Already Exists.",
                },
                status_code=400,
            )

    @staticmethod
    async def login_serv(data, db):
        email = data.email
        password = data.password

        # Fetch user by email
        user_details = AuthDAO.get_user_details_dao(email=email, db=db)

        if not user_details:
            return JSONResponse(
                content={"success": False, "message": "No user found with this email"},
                status_code=404,
            )

        # Verify password using bcrypt
        if not verify_password(password, user_details.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # Generate tokens
        access_token = create_access_token(
            {
                "user_id": user_details.id,
                "user_name": user_details.user_name,
                "email": user_details.email,
                "role_id": user_details.role_id,
            }
        )
        refresh_token = create_refresh_token(
            {
                "user_id": user_details.id,
                "user_name": user_details.user_name,
                "email": user_details.email,
                "role_id": user_details.role_id,
            }
        )

        # Login successful
        response = JSONResponse(
            content={
                "success": True,
                "message": f"Welcome {user_details.user_name}",
                "user_info": {
                    "user_id": user_details.id,
                    "user_name": user_details.user_name,
                },
            },
            status_code=200,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=15 * 60,
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7 days
            path="/refresh",  # refresh token only used in refresh endpoint
        )

        return response
