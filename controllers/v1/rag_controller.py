from services.v1.rag_services import RAGServices


class RAGController:
    @staticmethod
    async def ask_question_controller(data, db, created_by):
        query = data.get("question")
        is_new_chat = data.get("is_new_chat", False)
        if is_new_chat:
            chat_id = None
        else:
            chat_id = data.get("chat_id", None)
        return await RAGServices.ask_question_serv(
            query, is_new_chat, chat_id, db, created_by
        )

    @staticmethod
    async def upload_file_controller(files, db, created_by):
        return await RAGServices.upload_file_serv(files, db, created_by)

    @staticmethod
    async def get_chat_controller(chat_id, user_id, db, skip, limit):
        return await RAGServices.get_chat_serv(chat_id, user_id, db, skip, limit)

    @staticmethod
    async def get_document_list(uploaded_by: int, page: int, page_size: int, db):
        return await RAGServices.get_doc_list_serv(uploaded_by, page, page_size, db)

    @staticmethod
    async def get_chat_list_controller(user_id: int, db):
        return await RAGServices.get_chat_list_serv(user_id, db)
