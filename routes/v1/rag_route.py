from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    Depends,
    Query,
)
from database.v1.connection import getDBConnection
from controllers.v1.rag_controller import RAGController
from sqlalchemy.orm import Session
from typing import List
from middleware.v1.auth_token import token_required

router = APIRouter()


@router.post("/ask-ques")
async def ask_question(
    request: Request,
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):
    data = await request.json()
    created_by = current_user["user_id"]
    return await RAGController.ask_question_controller(data, db, created_by)


@router.post("/upload-pdf")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):

    created_by = current_user["user_id"]

    # Pass list of files to controller
    return await RAGController.upload_file_controller(files, db, created_by)


# Route 1: Without chat_id in path
@router.get("/get-messages")
async def get_messages_query(
    chat_id: int | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):
    skip = (page - 1) * limit
    user_id = current_user["user_id"]
    return await RAGController.get_chat_controller(chat_id, user_id, db, skip, limit)


# Route 2: chat_id in path
@router.get("/get-messages/{chat_id}")
async def get_messages_path(
    chat_id: int,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):
    skip = (page - 1) * limit
    user_id = current_user["user_id"]
    return await RAGController.get_chat_controller(chat_id, user_id, db, skip, limit)


@router.get("/doc-list")
async def get_document_list(
    uploaded_by: int = Query(None),
    page: int = Query(1, ge=1),  # default page=1
    page_size: int = Query(10, ge=1),  # default page_size=10
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):
    return await RAGController.get_document_list(uploaded_by, page, page_size, db)


@router.get("/get-chat-list")
async def get_chat_list(
    db: Session = Depends(getDBConnection),
    current_user: dict = Depends(token_required(required_permission=[(3, 2)])),
):
    user_id = current_user["user_id"]

    return await RAGController.get_chat_list_controller(user_id, db)
