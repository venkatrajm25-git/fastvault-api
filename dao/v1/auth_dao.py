from sqlalchemy.orm import Session
from models.v1.user_model import User


class AuthDAO:
    @staticmethod
    def register_user_dao(user_details, db: Session):
        new_user = User(
            email=user_details[0],
            password=user_details[1],
            user_name=user_details[2],
            role_id=user_details[3],
            status=user_details[4],
            created_by=user_details[5],
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id

    @staticmethod
    def get_user_details_dao(
        email: str = None, user_id: int = None, db: Session = None
    ):
        query = db.query(User).filter(User.is_deleted == 0)  # filter out deleted users

        if email:
            query = query.filter(User.email == email)

        if user_id:
            query = query.filter(User.id == user_id)

        if not email and not user_id:
            # no filters, return all active users
            return None

        return query.first()
