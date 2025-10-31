# from utils.v1.lang_utils import translate, translate_many, translate_pair
from model.v1.user_model import Role, Users

# from fastapi.responses import JSONResponse
# from model.v1.perm_model import Permission
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime

# import pytest


class IDGeneration:
    def userID(db: Session) -> int:
        last_id = db.query(func.max(Users.id)).scalar()
        return (last_id or 0) + 1


def serialize_data(data: dict):
    if not data:
        return data
    return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in data.items()}


# async def verifyID(id, db, accept_language):
#     # Check if the ID is None or empty
#     if id is None or str(id).strip() == "":
#         return JSONResponse(
#             content={
#                 **translate_pair("status", "false", lang=accept_language),
#                 **translate_pair("message", "id_missing", lang=accept_language),
#             },
#             status_code=400,
#         )
#     id = str(id).strip()  # Remove leading and trailing spaces

#     # Check if ID contains only digits
#     if not id.isdigit():
#         if " " in id:  # Check if there are spaces in the ID
#             return JSONResponse(
#                 content={
#                     **translate_pair("status", "false", lang=accept_language),
#                     **translate_pair(
#                         "message", "no_spaces_btw_digits", lang=accept_language
#                     ),
#                 },
#                 status_code=400,
#             )
#         return JSONResponse(
#             content={
#                 **translate_pair("status", "false", lang=accept_language),
#                 translate("message", lang=accept_language): translate_many(
#                     ["digits_only", "id"], lang=accept_language
#                 ),
#             },
#             status_code=400,
#         )

#     return JSONResponse(
#         content={
#             **translate_pair("status", "true", lang=accept_language),
#             translate("message", lang=accept_language): "ID Verified",
#         },
#         status_code=200,
#     )


# def fetchRecord(tablename, id, db: Session):
#     try:
#         query = text(f"SELECT * FROM {tablename} WHERE id = :id AND is_deleted = 0")
#         result = db.execute(query, {"id": id}).fetchone()

#         if result is None:
#             # pytest.fail(f"No record found with id {id}")  # Fails test if no record found
#             result = "No Data Found."
#             return result
#         else:
#             return result
#     except Exception as e:
#         pytest.fail(f"Error:{e}")


# def deletePermission(name, db: Session):
#     try:
#         db.query(Permission).filter(Permission.name == name).delete()
#         db.commit()
#         return True
#     except Exception as e:
#         pytest.fail(f"Error:{e}")


# def deleteTestingRecord(tablename, db: Session):
#     try:
#         query = text(f"DELETE FROM {tablename}")
#         db.execute(query)
#         db.commit()
#         return True
#     except Exception as e:
#         pytest.fail(f"Error:{e}")


# def deleteRole(role, db: Session):
#     try:
#         db.query(Role).filter(Role.rolename == role).delete()
#         db.commit()
#         return True
#     except Exception as e:
#         pytest.fail(f"Error:{e}")
