from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from config.v1.config_dev import getDBConnection
from model.v1.user_model import User
from model.v1.role_model import Role
from model.v1.permission_model import RolePermission, UserPermission
from config.v1.config import Config
from utils.v1.redis_client import is_token_blacklisted


def token_required(required_role: str = None, required_permission: tuple = None):
    async def dependency(request: Request, db: Session = Depends(getDBConnection)):
        # 1️⃣ Read token from cookie
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Token missing")

        # 2️⃣ Decode JWT
        try:
            payload = jwt.decode(
                token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )

            jti = payload.get("jti")

            if is_token_blacklisted(jti):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            user_id = payload.get("user_id")
            role_id = payload.get("role_id")
            email = payload.get("email")
            username = payload.get("username")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # 3️⃣ Check user exists
        user = db.query(User).filter_by(id=user_id, is_deleted=0).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 4️⃣ Role-based check (if required)
        role_name = (
            db.query(Role.role_name)
            .filter_by(id=role_id, is_deleted=0, status=1)
            .first()[0]
        )
        if required_role and role_name.lower() != required_role:
            raise HTTPException(status_code=403, detail="Permission denied.")

        # 5️⃣ Permission-based check (if required)
        if required_permission:
            module_id, permission_id = required_permission

            role_perm = (
                db.query(RolePermission)
                .filter_by(
                    role_id=role_id,
                    module_id=module_id,
                    permission_id=permission_id,
                    is_deleted=0,
                )
                .first()
            )

            if not role_perm:
                user_perm = (
                    db.query(UserPermission)
                    .filter_by(
                        user_id=user_id,
                        module_id=module_id,
                        permission_id=permission_id,
                        is_deleted=0,
                    )
                    .first()
                )
                if not user_perm:
                    raise HTTPException(
                        status_code=403,
                        detail="Permission denied.",
                    )

        # 6️⃣ Return lightweight user info
        return {
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role_name,
        }

    return dependency
