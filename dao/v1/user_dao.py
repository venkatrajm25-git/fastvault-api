from fastapi.responses import JSONResponse
from model.v1.user_model import User, PasswordResetToken
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class user_databaseConnection:
    @staticmethod
    def registerUserDetails(user_data, role, db: Session):
        # Establishing a database connection
        try:
            user_id, email, hashedPwd, username, status, created_by_email = user_data
            if role:
                newUser = User(
                    id=user_id,
                    email=email,
                    pwd=hashedPwd,
                    username=username,
                    status=status,
                    created_by=created_by_email,
                    role=role,
                )
            else:
                newUser = User(
                    id=user_id,
                    email=email,
                    pwd=hashedPwd,
                    username=username,
                    status=status,
                    created_by=created_by_email,
                )

            db.add(newUser)
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={"message": "User Created Successfully.", "success": True},
                status_code=201,
            )
        except IntegrityError as ie:
            db.rollback()
            # Optional: check for specific error codes
            if "1062" in str(ie.orig):
                return JSONResponse(
                    content={"success": False, "error": "Duplicate entry"},
                    status_code=400,
                )
            elif "1452" in str(ie.orig):  # foreign key constraint fail
                return JSONResponse(
                    content={"success": False, "error": "Foreign key not existed."},
                    status_code=400,
                )
            else:
                return JSONResponse(
                    content={"success": False, "error": "Database integrity error"},
                    status_code=400,
                )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )

    @staticmethod
    def getUserTable(db: Session):
        # Establishing a database connection
        try:
            result = db.query(User).filter(User.is_deleted == 0).all()
            return result  # Returning user data
        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": "Database Connection Error."},
                status_code=400,
            )

    @staticmethod
    def updateUser(id, updateUser, dataList, db: Session):
        try:
            updateData = dict(zip(updateUser, dataList))
            result = db.query(User).filter(User.id == id).update(updateData)
            db.commit()
            if result == 0:
                return False  # No rows were updated
            return True
        except Exception as e:
            return False

    @staticmethod
    def deleteUserDB(id, db: Session):
        try:
            result = db.query(User).filter(User.id == id).update({"is_deleted": 1})
            db.commit()
            if result == 0:
                return False  # No user found to delete
            return True
        except Exception as e:
            return False

    @staticmethod
    def addResetPasswordToken(dataList, db: Session):
        try:
            ExistingUserID = (
                db.query(PasswordResetToken)
                .filter(PasswordResetToken.user_id == dataList[0])
                .first()
            )
            if ExistingUserID:
                db.query(PasswordResetToken).filter(
                    PasswordResetToken.user_id == dataList[0]
                ).update(
                    {"token": dataList[1], "expires_at": dataList[2], "used": False}
                )
                db.commit()
            else:
                newResetToken = PasswordResetToken(
                    user_id=dataList[0],
                    token=dataList[1],
                    expires_at=dataList[2],
                )
                db.add(newResetToken)
                db.commit()
            return JSONResponse(
                content={"message": "Added Reset Password Successfully"},
                status_code=201,
            )
        except Exception as e:
            return JSONResponse(
                content={"message": "Reset Password not added."},
                status_code=400,
            )
