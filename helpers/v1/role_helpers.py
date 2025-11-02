# from dao.v1.role_dao import Role_DBConn
# from fastapi.responses import JSONResponse


# async def verifyRoleID(id, db, accept_language):
#     # Check if the Role ID is None or empty
#     # if not id:
#     #     return JSONResponse(
#     #         content={
#     #             **translate_pair("success", "false", lang=accept_language),
#     #             translate("message", lang=accept_language): translate_many(
#     #                 ["role", "id_missing"], lang=accept_language
#     #             ),
#     #         },
#     #         status_code=400,
#     #     )

#     # id = id.strip()  # Remove leading and trailing spaces

#     data = [
#         i.id for i in Role_DBConn.getRoleData(db)
#     ]  # Fetch existing Role IDs from the database

#     # Check if the given Role ID exists in the database
#     if id not in data:
#         return JSONResponse(
#             content={
#                 **translate_pair("success", "false", lang=accept_language),
#                 translate("message", lang=accept_language): translate_many(
#                     ["role", "id", "not_available"], lang=accept_language
#                 ),
#             },
#             status_code=400,
#         )

#     return JSONResponse(
#         content={
#             **translate_pair("success", "true", lang=accept_language),
#             translate("message", lang=accept_language): "Role ID Verified",
#         },
#         status_code=200,
#     )
