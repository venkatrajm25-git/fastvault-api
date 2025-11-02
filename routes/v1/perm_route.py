from controllers.v1.perm_controller import PermissionModule
from fastapi import APIRouter, Request, Query, Depends, Header
from middleware.v1.auth_token import token_required
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection
from audit_trail.v1.audit_decorater import audit_loggable
from model.v1.permission_model import RolePermission, UserPermission, Permission

router = APIRouter()


@router.get("/getrolepermission")
async def get_role_permission(
    role_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.getRolePermission(role_id, db, accept_language)


@router.post("/addrolepermission")
@audit_loggable(
    action="CREATE",
    table_name="role_permissions",
    model_class=RolePermission,
)
async def add_role_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = await request.json()
    return await PermissionModule.addRolePermission(data, db, accept_language)


@router.patch("/updaterolepermission")
@audit_loggable(
    action="UPDATE",
    table_name="role_permissions",
    model_class=RolePermission,
    id_field="rp_id",
)
async def update_role_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = getattr(request, "_json", None) or await request.json()
    return await PermissionModule.updateRolePermission(data, db, accept_language)


@router.delete("/deleterolepermission")
@audit_loggable(
    action="DELETE",
    table_name="role_permissions",
    model_class=RolePermission,
    id_field="rp_id",
)
async def delete_role_permission(
    rp_id: int = Query(...),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):

    return await PermissionModule.deleteRolePermission(rp_id, db, accept_language)


@router.get("/getsingleuserperm")
async def get_single_user_permission(
    email: str = Query(None),
    user_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.getSingleUserPermission(
        email, user_id, db, accept_language
    )


@router.post("/adduserpermission")
@audit_loggable(
    action="CREATE",
    table_name="user_permissions",
    model_class=UserPermission,
)
async def add_user_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = await request.json()
    return await PermissionModule.addUserPermission(data, db, accept_language)


@router.get("/getuserpermission")
async def get_user_permission(
    user_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.getUserPermission(user_id, db, accept_language)


@router.patch("/updateuserpermission")
@audit_loggable(
    action="UPDATE",
    table_name="user_permissions",
    model_class=UserPermission,
    id_field="up_id",
)
async def update_user_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = getattr(request, "_json", None) or await request.json()
    return await PermissionModule.updateUserPermission(data, db, accept_language)


@router.delete("/deleteuserpermission")
@audit_loggable(
    action="DELETE",
    table_name="user_permissions",
    model_class=UserPermission,
    id_field="up_id",
)
async def delete_user_permission(
    up_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.deleteUserPermission(up_id, db, accept_language)


@router.post("/addpermission")
@audit_loggable(
    action="CREATE",
    table_name="permission_table",
    model_class=Permission,
)
async def add_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = await request.json()
    add_perm_data = {"name": data.get("name"), "current user": current_user}
    return await PermissionModule.addPermission(add_perm_data, db, accept_language)


@router.get("/getpermission")
async def get_permission(
    permission_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.getPermission(permission_id, db, accept_language)


@router.patch("/updatepermission")
@audit_loggable(
    action="UPDATE",
    table_name="permission_table",
    model_class=Permission,
    id_field="permission_id",
)
async def update_permission(
    request: Request,
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    data = getattr(request, "_json", None) or await request.json()
    return await PermissionModule.updatePermission(
        data, db, accept_language, current_user
    )


@router.delete("/deletepermission")
@audit_loggable(
    action="DELETE",
    table_name="permission_table",
    model_class=Permission,
    id_field="permission_id",
)
async def delete_permission(
    permission_id: int = Query(None),
    current_user: dict = Depends(token_required(required_role="admin")),
    db: Session = Depends(getDBConnection),
    accept_language: str = Header(default="en"),
):
    return await PermissionModule.deletePermission(permission_id, db, accept_language)
