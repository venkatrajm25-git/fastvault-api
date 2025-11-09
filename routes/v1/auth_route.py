from sqlalchemy.orm import Session
from config.v1.config_dev import getDBConnection
from controllers.v1.auth_controller import AuthController
from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Header,
    BackgroundTasks,
    Query,
    HTTPException,
)
from model.v1.user_model import User
from schema.v1.auth_schema import (
    RegisterUserBaseModel,
    LoginUserBaseModel,
    ResetPassBaseModel,
)
import jwt
from config.v1.config import Config
from dao.v1.auth_dao import AuthDAO
from middleware.v1.auth_token import token_required
from utils.v1.token_generation import create_access_token
from utils.v1.auth_utils import verifyResetPassToken
from utils.v1.audit_logger import log_audit
from utils.v1.redis_client import blacklist_token

router = APIRouter()


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


#! delete this
@router.get("/dummy-route")
async def dummy_route(
    db: Session = Depends(getDBConnection),
    user: dict = Depends(token_required(required_role="admin")),
):
    user_id = user.get("user_id")
    data = db.query(User).filter(User.id == user_id).first()
    return {"user_name": data.user_name, "message": "Route Working."}


@router.post("/forgetpassword", name="forget_password")
async def forgot_password(
    request: Request,
    background_task: BackgroundTasks,
    db: Session = Depends(getDBConnection),
):
    data = await request.json()
    email = data.get("email", "")
    return AuthController.forgetPassword(email, request, background_task, db)


@router.get("/reset-password")
async def verify_reset_pass_token(
    token: str = Query(...), db: Session = Depends(getDBConnection)
):
    token_row = await verifyResetPassToken(token, db)
    return {"success": True, "message": "Valid link"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPassBaseModel,
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await AuthController.resetPasswordSubmit(data, db)


@router.post("/logout")
async def logout(
    request: Request,
    user: dict = Depends(token_required()),
    db: Session = Depends(getDBConnection),
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token and not refresh_token:
        raise HTTPException(status_code=400, detail="Tokens Missing.")

    if access_token:
        blacklist_token(access_token)
    if refresh_token:
        blacklist_token(refresh_token)

    try:
        await log_audit(
            db=db,
            table_name="users",
            record_id=user.id,
            action="LOGOUT",
            user=user.id,
            request=request,
            old_data=None,
            new_data=None,
        )
    except Exception:
        pass

    response = JSONResponse(
        content={"success": True, "message": "Logged Out Successfully."}
    )

    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response
