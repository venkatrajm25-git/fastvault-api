from fastapi import APIRouter, Query, Request, Depends, Header
from middleware.v1.auth_token import token_required
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from model.v1.user_model import Users
from database.v1.connection import getDBConnection
from controllers.v1.user_controller import UserController
from audit_trail.v1.audit_decorater import audit_loggable
from typing import Optional

from schema.v1.auth_base_schema import UpdateUserRequest


router = APIRouter()


@router.get("/getuser")
async def get_user(
    id: Optional[int] = Query(None),
    current_user: dict = Depends(token_required(required_permission=[(2, 2)])),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await UserController.getAllUser(id, db, accept_language)


@router.patch("/updateuser")
@audit_loggable(
    action="UPDATE",
    table_name="users",
    model_class=Users,
    id_field="id",
)
async def update_user(
    payload: UpdateUserRequest,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await UserController.updateUser(payload, db, accept_language, current_user)


@router.delete("/deleteuser")
@audit_loggable(
    action="DELETE",
    table_name="users",
    model_class=Users,
    id_field="id",
)
async def delete_user(
    id: int = Query(...),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await UserController.deleteUser(id, db, accept_language)
