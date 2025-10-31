from controllers.v1.perm_controller import PermissionModule
from fastapi import APIRouter, Request, Depends, Query, Header
from middleware.v1.auth_token import token_required
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection
from audit_trail.v1.audit_decorater import audit_loggable
from model.v1.module_model import Module

router = APIRouter()


@router.post("/addmodule")
@audit_loggable(
    action="CREATE",
    table_name="module_table",
    model_class=Module,
)
async def add_module(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = await request.json()
    add_module_data = {"name": data.get("name"), "user": current_user}
    return await PermissionModule.addModule(
        add_module_data, db, accept_language, current_user
    )


@router.get("/getmodule")
async def get_module(
    module_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.getModule(module_id, db, accept_language)


@router.patch("/updatemodule")
@audit_loggable(
    action="UPDATE",
    table_name="module_table",
    model_class=Module,
    id_field="module_id",
)
async def update_module(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = getattr(request, "_json", None) or await request.json()
    return await PermissionModule.updateModule(data, db, accept_language, current_user)


@router.delete("/deletemodule")
@audit_loggable(
    action="DELETE",
    table_name="module_table",
    model_class=Module,
    id_field="module_id",
)
async def delete_module(
    module_id: int = Query(...),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.deleteModule(module_id, db, accept_language)
