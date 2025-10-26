from fastapi import APIRouter, Depends, Request
from config.v1.config_dev import getDBConnection
from sqlalchemy.orm import Session
from models.v1.user_model import User
from fastapi import HTTPException
from controllers.v1.auth_controller import AuthController
from schema.v1.auth_schema import RegisterUserBaseModel, LoginUserBaseModel
import jwt
from config.v1.config import Config
from dao.v1.auth_dao import AuthDAO
from middleware.v1.token_creation import create_access_token
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(getDBConnection)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(
            refresh_token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        user_details = AuthDAO.get_user_details_dao(user_id=user_id, db=db)
        if not user_details:
            raise HTTPException(status_code=401, detail="User not found")
        new_access_token = create_access_token(
            {
                "user_id": user_details.id,
                "user_name": user_details.user_name,
                "email": user_details.email,
                "role_id": user_details.role_id,
            }
        )
        # new_access_token = create_access_token({"user_id": user.id})
        response = JSONResponse(content={"success": True})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=15 * 60,
            path="/",
        )
        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")


@router.post("/register")
async def register_user(
    data: RegisterUserBaseModel, db: Session = Depends(getDBConnection)
):
    return await AuthController.register_controller(data, db)


@router.post("/login")
async def login(data: LoginUserBaseModel, db: Session = Depends(getDBConnection)):
    return await AuthController.login_controller(data, db)
