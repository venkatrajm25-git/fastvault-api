from model.v1.rag_model import RAG_Model, RAGDataset, Chat
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


class RAG_DAO:
    @staticmethod
    def save_question(query, created_by, db: Session, chat_id):
        saveQues = RAG_Model(question=query, created_by=created_by, chat_id=chat_id)
        db.add(saveQues)
        db.commit()
        db.refresh(saveQues)
        return saveQues.id

    @staticmethod
    def save_answer(ques_id: int, answer: str, db: Session):
        # fetch the question entry
        entry = db.query(RAG_Model).filter(RAG_Model.id == ques_id).first()
        if not entry:
            raise ValueError(f"Question with id {ques_id} not found")

        # update answer and timestamp
        entry.answer = answer
        entry.ans_created_at = func.now()

        db.commit()
        db.refresh(entry)
        return entry.id

    @staticmethod
    def get_chat_dao(
        user_id: int, chat_id: int, db: Session, skip: int = 0, limit: int = 20
    ):
        chat_data = (
            db.query(RAG_Model)
            .filter(
                RAG_Model.created_by == user_id,
                RAG_Model.is_deleted == 0,
                RAG_Model.chat_id == chat_id,
            )
            .order_by(
                func.coalesce(
                    RAG_Model.ans_created_at, RAG_Model.ques_created_at
                ).desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return chat_data

    @staticmethod
    def get_doc_list_dao(db: Session):
        # docList = db.query(RAGDataset).all()
        # return docList
        docList = db.query(RAGDataset).order_by(RAGDataset.uploaded_at.desc()).all()
        return docList

    @staticmethod
    def create_chat(chat_title, created_by, db: Session):
        new_chat = Chat(chat_name=chat_title, created_by=created_by)
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        return new_chat

    @staticmethod
    def get_latest_chat_by_user(user_id, db: Session):
        return (
            db.query(Chat)  # Chat is your chats table model
            .filter(Chat.created_by == user_id, Chat.is_deleted == 0)
            .order_by(Chat.created_at.desc())  # Get the most recent chat
            .first()  # Return single chat or None
        )

    @staticmethod
    def get_all_chats_with_last_activity(user_id: int, db: Session):
        from sqlalchemy.sql import func

        return (
            db.query(
                Chat.chat_id,
                Chat.chat_name,
                func.max(
                    func.coalesce(RAG_Model.ans_created_at, RAG_Model.ques_created_at)
                ).label("last_activity"),
            )
            .join(RAG_Model, Chat.chat_id == RAG_Model.chat_id)
            .filter(
                Chat.created_by == user_id,
                Chat.is_deleted == 0,
                RAG_Model.is_deleted == 0,
            )
            .group_by(Chat.chat_id, Chat.chat_name)
            .order_by(
                func.max(
                    func.coalesce(RAG_Model.ans_created_at, RAG_Model.ques_created_at)
                ).desc()
            )
            .all()
        )

    @staticmethod
    def get_chat_by_id(chat_id, created_by, db: Session):
        chat = (
            db.query(Chat)
            .filter(
                Chat.chat_id == chat_id,
                Chat.created_by == created_by,
                Chat.is_deleted == 0,
            )
            .first()
        )
        return chat
