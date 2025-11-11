# from controllers.v1.blog_controller import Services
from fastapi import APIRouter, Query, Request, Depends, Header
from schema.v1.role_base_schema import UpdateRole
from middleware.v1.auth_token import token_required
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection
from audit_trail.v1.audit_decorater import audit_loggable
from model.v1.user_model import Role
from controllers.v1.role_controller import RoleController


router = APIRouter()


# roleBP.route('/getrole', methods=['GET'], endpoint="get_role")(Services.getRole)
@router.get("/getrole")
async def get_role(
    role_id: int = Query(None),
    current_user: dict = Depends(token_required(required_permission=[(1, 2)])),
    db: Session = Depends(getDBConnection),
):
    return await RoleController.getRole(role_id, db)


# roleBP.route('/addrole', methods=['POST'], endpoint="add_role")(Services.addrole)
@router.post("/addrole")
@audit_loggable(
    action="CREATE",
    table_name="roles",
    model_class=Role,
)
async def add_role(
    request: Request,
    current_user: dict = Depends(token_required(required_permission=[(1, 1)])),
    db: Session = Depends(getDBConnection),
):
    data = await request.json()
    return RoleController.addrole(data, db, current_user)


@router.patch("/updaterole")
@audit_loggable(
    action="UPDATE",
    table_name="roles",
    model_class=Role,
    id_field="role_id",
)
async def update_role(
    data: UpdateRole,
    current_user: dict = Depends(token_required(required_permission=[(1, 3)])),
    db: Session = Depends(getDBConnection),
):
    return await RoleController.updateRole(data, db, current_user)


@router.delete("/deleterole")
@audit_loggable(
    action="DELETE",
    table_name="roles",
    model_class=Role,
    id_field="role_id",
)
async def delete_role(
    role_id: int = Query(...),
    current_user: dict = Depends(token_required(required_permission=[(1, 4)])),
    db: Session = Depends(getDBConnection),
):

    return await RoleController.deleteRole(role_id, db)
