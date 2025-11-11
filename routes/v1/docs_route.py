from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from main import app
from fastapi.security import HTTPBasicCredentials, HTTPBasic


router = APIRouter()

# simple local security instance
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "secret@321"
    if not (
        credentials.username == correct_username
        and credentials.password == correct_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/docs", include_in_schema=False)
async def custom_swagger_url(
    userinfo: dict = Depends(get_current_username),
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="RAG Concept Docs")


@router.get("/redoc", include_in_schema=False)
async def custom_redoc(
    user_info: dict = Depends(get_current_username),
):
    return get_redoc_html(openapi_url="/openapi.json", title="Concept RAG ReDoc")


@router.get("/openapi.json", include_in_schema=False)
async def custom_openapi(
    user_info: dict = Depends(get_current_username),
):
    return get_openapi(title="Concept RAG", version="1.0.0", routes=app.routes)
