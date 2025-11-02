from . import (
    auth_route,
    docs_route,
    module_route,
    perm_route,
    role_route,
    user_route,
)
from fastapi import FastAPI


def register_routes(app: FastAPI):
    app.include_router(docs_route.router)
    app.include_router(auth_route.router, prefix="/v1/auth", tags=["Auth"])
    app.include_router(module_route.router, prefix="/v1/module", tags=["Module"])
    app.include_router(perm_route.router, prefix="/v1/perm", tags=["Permission"])
    app.include_router(role_route.router, prefix="/v1/role", tags=["Role"])
    app.include_router(user_route.router, prefix="/v1/user", tags=["User"])
