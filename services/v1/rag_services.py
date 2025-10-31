# FAISS setup
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi.responses import JSONResponse
import requests
import uuid
from sqlalchemy import func
from datetime import datetime, timedelta
import asyncio
from model.v1.user_model import Users
from model.v1.rag_model import RAGDataset, RAG_Model, Chat
from sqlalchemy.orm import Session
from utils.v1.rag_utils import load_pdfs
from dao.v1.rag_dao import RAG_DAO
import math
import re
from configs.v1.config import ConfigClass


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
pdf_folder = "uploaded_pdfs"

try:
    embeddings = HuggingFaceEmbeddings(model_name=ConfigClass.OPENAI_EMBEDDING_MODEL)
except Exception as e:
    print("Embedding model not found.")


def slugify(text: str) -> str:
    """Convert text to URL-safe format."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)  # remove special chars
    text = re.sub(r"[\s]+", "-", text)  # replace spaces with -
    return text


def openai_chat(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
    }
    # ⚡ bypass SSL
    resp = requests.post(url, headers=headers, json=data, verify=False)
    return resp.json()["choices"][0]["message"]["content"]


class RAGServices:
    @staticmethod
    async def ask_question_serv(query, is_new_chat, chat_id, db: Session, created_by):
        try:
            docs = []

            # --------- Step 1: Determine which chat to use ---------
            chat = None

            if chat_id:  # ✅ Use provided chat_id if available
                chat = RAG_DAO.get_chat_by_id(chat_id, created_by, db)

            if not chat and not is_new_chat:
                # Otherwise, try to get the user's latest chat
                chat = RAG_DAO.get_latest_chat_by_user(created_by, db)

            if not chat:
                # Create a new chat if none exists
                prompt_title = f"Create a short, descriptive chat title (max 5 words) for this user question: '{query}'"
                try:
                    chat_title = openai_chat(prompt_title).strip()
                    if chat_title.startswith('"') and chat_title.endswith('"'):
                        chat_title = chat_title[1:-1].strip()
                    if not chat_title:
                        raise ValueError("Empty title from AI")
                except Exception as e:
                    print(f"AI failed, fallback to default: {e}")
                    from datetime import datetime

                    chat_title = (
                        f"New Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    )

                chat = RAG_DAO.create_chat(chat_title, created_by, db)

            chat_id = chat.chat_id

            # --------- Step 2: Save Question in DB ---------
            ques_id = RAG_DAO.save_question(query, created_by, db, chat_id=chat_id)

            # --------- Step 3: Load PDF docs asynchronously ---------
            docs = await asyncio.to_thread(load_pdfs)

            if not docs:
                return JSONResponse(
                    content={"error": "No documents could be processed"},
                    status_code=400,
                )

            # --------- Step 4: Split docs & setup FAISS retriever ---------
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=6000, chunk_overlap=600
            )
            split_docs = splitter.split_documents(docs)

            faiss_db = FAISS.from_documents(split_docs, embeddings)
            retriever = faiss_db.as_retriever(search_kwargs={"k": 2})

            # --------- Step 5: Retrieve context and ask GPT ---------
            results = faiss_db.similarity_search(query, k=1)
            context = "\n".join([r.page_content for r in results])

            prompt_answer = f"Answer strictly based on the following context:\n{context}\n\nQuestion: {query}"
            answer = openai_chat(prompt_answer)

            # --------- Step 6: Save Answer in DB ---------
            RAG_DAO.save_answer(ques_id, answer, db)

            return JSONResponse(
                content={
                    "success": True,
                    "message": "Chat added successfully.",
                    "chat_id": chat.chat_id,
                    "chat_title": chat.chat_name,
                    "question": query,
                    "answer": answer,
                },
                status_code=201,
            )

        except Exception as e:
            return JSONResponse(
                content={"error": str(e)},
                status_code=500,
            )

    @staticmethod
    async def upload_file_serv(files, db: Session, created_by):
        results = []

        for file in files:
            try:
                name, ext = os.path.splitext(file.filename)

                # ✅ Validate file type (optional, if you want only PDFs)
                if ext.lower() != ".pdf":
                    results.append(
                        {
                            "filename": file.filename,
                            "path": None,
                            "status": "error",
                            "message": f"{file.filename} is not a PDF file.",
                        }
                    )
                    continue

                slug_name = slugify(name)
                unique_id = uuid.uuid4().hex[:8]  # 8 chars
                stored_filename = f"{slug_name}_{unique_id}{ext}"
                file_path = os.path.join(pdf_folder, stored_filename)

                # ✅ Save the file
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)

                # ✅ Insert into DB
                newPDFFile = RAGDataset(
                    original_filename=file.filename,
                    filepath=file_path,
                    stored_filename=stored_filename,
                    uploaded_by=created_by,
                )
                db.add(newPDFFile)
                db.commit()
                db.refresh(newPDFFile)

                results.append(
                    {
                        "filename": file.filename,
                        "path": file_path,
                        "status": "success",
                        "message": "File uploaded successfully.",
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "filename": file.filename,
                        "path": None,
                        "status": "error",
                        "message": str(e),
                    }
                )

        # ✅ Count successes and failures
        success_count = len([r for r in results if r["status"] == "success"])
        fail_count = len([r for r in results if r["status"] == "error"])

        # ✅ Determine message based on result
        if success_count == len(results):
            response_message = "All files uploaded successfully."
            success_flag = True
        elif fail_count == len(results):
            response_message = "All file uploads failed."
            success_flag = False
        else:
            response_message = (
                "Some files were uploaded successfully, while others failed."
            )
            success_flag = False

        return JSONResponse(
            content={
                "success": success_flag,
                "message": response_message,
                "files": results,
            }
        )

    @staticmethod
    async def get_chat_serv(chat_id, user_id, db: Session, skip, limit):
        try:
            if chat_id:
                chat = (
                    db.query(Chat)
                    .filter(Chat.chat_id == chat_id, Chat.created_by == user_id)
                    .first()
                )
            else:
                chat = RAG_DAO.get_latest_chat_by_user(user_id, db)
                chat_id = chat.chat_id if chat else None

            if not chat:
                return JSONResponse(
                    content={"success": True, "message": "No chat found for this user."}
                )

            # Extract chat_name from chat record
            chat_name = chat.chat_name

            # Fetch username
            user_name = db.query(Users).filter(Users.id == user_id).first().username

            # Fetch chat rows and reverse
            chat_rows = RAG_DAO.get_chat_dao(user_id, chat_id, db, skip, limit)
            chat_data = list(reversed(chat_rows))

            chat_list = []
            for row in chat_data:
                chat_list.append(
                    {
                        "id": row.id,
                        "question": row.question,
                        "answer": row.answer,
                        "ques_created_at": (
                            row.ques_created_at.isoformat()
                            if row.ques_created_at
                            else None
                        ),
                        "ans_created_at": (
                            row.ans_created_at.isoformat()
                            if row.ans_created_at
                            else None
                        ),
                    }
                )

            # Count total records
            total_count = (
                db.query(func.count(RAG_Model.id))
                .filter(
                    RAG_Model.created_by == user_id,
                    RAG_Model.is_deleted == 0,
                    RAG_Model.chat_id == chat_id,
                )
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_count + limit - 1) // limit

            # Final response
            response = {
                "success": True,
                "user_id": user_id,
                "username": user_name,
                "chat_id": chat_id,
                "chat_name": chat_name,
                "chat": chat_list if chat_list else "No Record Found.",
                "pagination": {
                    "total_records": total_count,
                    "total_pages": total_pages,
                    "current_page": (skip // limit) + 1,
                    "limit": limit,
                },
            }

            return response
        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )

    @staticmethod
    async def get_doc_list_serv(uploaded_by, page, page_size, db):
        try:
            docList = RAG_DAO.get_doc_list_dao(db)

            # Get page and page_size (default values: page=1, page_size=10)

            # Filter by uploaded_by if provided
            dataList = []
            if uploaded_by:
                for i in docList:
                    if i.uploaded_by == uploaded_by:
                        dataList.append(
                            {
                                "file_id": i.id,
                                "file_name": i.original_filename,
                                "file_path": i.filepath,
                                "uploaded_by": i.uploaded_by,
                                "uploaded_at": i.uploaded_at.isoformat(),
                            }
                        )
                message = (
                    "Fetched document uploaded by this user."
                    if dataList
                    else "No files uploaded by this user."
                )
            else:
                for i in docList:
                    dataList.append(
                        {
                            "file_id": i.id,
                            "file_name": i.original_filename,
                            "file_path": i.filepath,
                            "uploaded_by": i.uploaded_by,
                            "uploaded_at": i.uploaded_at.isoformat(),
                        }
                    )
                message = "Fetched Document List" if dataList else "No files found."

            # Pagination logic
            total_records = len(dataList)
            total_pages = math.ceil(total_records / page_size) if page_size else 1

            start = (page - 1) * page_size
            end = start + page_size
            paginated_data = dataList[start:end]

            return JSONResponse(
                content={
                    "success": True,
                    "message": message,
                    "data": paginated_data,
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_records": total_records,
                }
            )

        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )

    @staticmethod
    async def get_chat_list_serv(user_id, db):
        try:
            chats = RAG_DAO.get_all_chats_with_last_activity(user_id, db)

            today = datetime.now().date()
            yesterday = today - timedelta(days=1)

            today_chats = []
            yesterday_chats = []
            previous_chats = []

            for chat in chats:
                if not chat.last_activity:
                    continue

                last_activity_date = chat.last_activity.date()

                chat_info = {
                    "chat_id": chat.chat_id,
                    "chat_name": chat.chat_name,
                    "last_activity": chat.last_activity.isoformat(),
                }

                if last_activity_date == today:
                    today_chats.append(chat_info)
                elif last_activity_date == yesterday:
                    yesterday_chats.append(chat_info)
                else:
                    previous_chats.append(chat_info)

            # Build chat_list dynamically
            chat_list = {}
            if today_chats:
                chat_list["today"] = today_chats
            if yesterday_chats:
                chat_list["yesterday"] = yesterday_chats
            if previous_chats:
                chat_list["last_week"] = previous_chats

            return JSONResponse(
                content={
                    "user_id": user_id,
                    "success": True,
                    "message": "Chat list fetched successfully.",
                    "chat_list": chat_list,
                }
            )

        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )


# @staticmethod
#     async def ask_question_serv(query, db: Session, created_by):
#         try:
#             docs = []
#             # Save Question in DB
#             ques_id = RAG_DAO.save_question(query, created_by, db)

#             # Run the synchronous function in a thread pool
#             # * load_pdfs from rag_utils
#             docs = await asyncio.to_thread(load_pdfs)

#             # print(f"Loaded {len(docs)} documents from PDFs.")

#             if not docs:
#                 return JSONResponse(
#                     content={"error": "No documents could be processed"},
#                     status_code=400,
#                 )

#             splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=6000, chunk_overlap=600
#             )
#             split_docs = splitter.split_documents(docs)

#             faiss_db = FAISS.from_documents(split_docs, embeddings)
#             retriever = faiss_db.as_retriever(search_kwargs={"k": 2})

#             def openai_chat(prompt):
#                 url = "https://api.openai.com/v1/chat/completions"
#                 headers = {
#                     "Authorization": f"Bearer {OPENAI_API_KEY}",
#                     "Content-Type": "application/json",
#                 }
#                 data = {
#                     "model": "gpt-3.5-turbo",
#                     "messages": [{"role": "user", "content": prompt}],
#                 }
#                 # ⚡ bypass SSL
#                 resp = requests.post(url, headers=headers, json=data, verify=False)
#                 return resp.json()["choices"][0]["message"]["content"]

#             # Retrieve context from FAISS
#             # query = "So today I need to go earlier from office. so i asked for permission and got it for 2 hours. so now what is the time i can leave from office?"
#             results = faiss_db.similarity_search(query, k=1)
#             context = "\n".join([r.page_content for r in results])

#             # Ask GPT using retrieved context
#             prompt = f"Answer strictly based on the following context:\n{context}\n\nQuestion: {query}"
#             answer = openai_chat(prompt)

#             # Save Answer in DB
#             RAG_DAO.save_answer(ques_id, answer, db)

#             return JSONResponse(
#                 content={"success": True, "message": "Chat added successfully."},
#                 status_code=201,
#             )

#         except Exception as e:
#             return JSONResponse(content={"error": str(e)}, status_code=400)
