from model.v1.perm_model import Permission, RolePermission, UserPermission
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.v1.lang_utils import translate, translate_many, translate_pair


class Permissions_DBConn:
    @staticmethod
    def getPermissionData(db: Session):
        # Establishing a database connection
        data = (
            db.query(Permission).filter(Permission.is_deleted == 0).all()
        )  # Query to fetch all permission records
        return data  # Returning the fetched data

    @staticmethod
    def addPermissionDB(name, created_by, db: Session):
        try:
            # Query to insert a new permission record
            newPermission = Permission(name=name, created_by=created_by)
            db.add(newPermission)
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={"success": True, "message": "Permission added"},
                status_code=201,
            )  # Returning the result
        except IntegrityError as ie:
            db.rollback()
            # Optional: check for specific error codes
            return JSONResponse(
                content={"success": False, "error": "Database integrity error"},
                status_code=400,
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )

    @staticmethod
    def updatePermissionDB(recentUpdate, data2update, permission_id, db: Session):
        try:
            updateData = dict(zip(recentUpdate, data2update))
            db.query(Permission).filter(Permission.id == permission_id).update(
                updateData
            )
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Permission updated successfully.",
                },
                status_code=200,
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
            )  # Returning the result

    @staticmethod
    def deletePermissionDB(perm_id, db: Session):
        try:
            data = True  # Default return value indicating success
            db.query(Permission).filter(Permission.id == perm_id).update(
                {"is_deleted": 1}
            )
            db.commit()  # Committing the transaction
        except Exception as e:
            print(e)  # Printing the error if an exception occurs
            data = "Error"  # Returning "Error" in case of an exception
        return data  # Returning the result


class RolePerm_DBConn:
    @staticmethod
    def getRPData(db: Session):
        # Establishing a database connection
        try:
            data = db.query(RolePermission).filter(RolePermission.is_deleted == 0).all()
            return data  # Returning the fetched data
        except Exception as e:
            return []

    @staticmethod
    def addRolePerm(dataList, db: Session, accept_language):
        try:
            # Query to insert a new role permission record
            newRolePermission = RolePermission(
                role_id=dataList[0], module_id=dataList[1], permission_id=dataList[2]
            )
            db.add(newRolePermission)
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["role", "permission", "added_successfully"],
                        lang=accept_language,
                    ),
                },
                status_code=201,
            )
        except IntegrityError as ie:
            db.rollback()
            # Optional: check for specific error codes
            # if "1062" in str(ie.orig):
            #     return JSONResponse(
            #         content={"success": False, "error": "Duplicate entry"},
            #         status_code=400,
            #     )
            # else:
            return JSONResponse(
                content={"success": False, "error": "Database integrity error"},
                status_code=400,
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=400
            )

    @staticmethod
    def updateRolePermissionDB(
        recentUpdate, data2update, id, db: Session, accept_language
    ):
        try:
            updateData = dict(zip(recentUpdate, data2update))
            db.query(RolePermission).filter(RolePermission.id == id).update(updateData)
            db.commit()  # Committing the transaction
            updated_data = {
                recentUpdate[i]: data2update[i] for i in range(len(recentUpdate))
            }
            return JSONResponse(
                content={
                    **translate_pair("success", "true", lang=accept_language),
                    translate("message", lang=accept_language): translate_many(
                        ["role", "permission", "updated_successfully"]
                    ),
                    "updated_fields": updated_data,
                },
                status_code=201,
            )
        except IntegrityError as ie:
            db.rollback()
            # Optional: check for specific error codes
            if "1062" in str(ie.orig):
                return JSONResponse(
                    content={
                        **translate_pair("success", "false", lang=accept_language),
                        translate("message", lang=accept_language): translate_many(
                            ["role", "permission", "already_exists"]
                        ),
                    },
                    status_code=400,
                )
            elif "1452" in str(ie.orig):  # foreign key constraint fail
                return JSONResponse(
                    content={"error": "Foreign key not existed."}, status_code=400
                )
            else:
                return JSONResponse(
                    content={"error": "Database integrity error"}, status_code=400
                )

        except Exception as e:
            return JSONResponse(
                content={
                    **translate_pair("success", "false", lang=accept_language),
                    "message": str(e),
                },
                status_code=400,
            )

    @staticmethod
    def deleteRp(rp_id, db: Session):
        # Establishing a database connection
        try:
            db.query(RolePermission).filter(RolePermission.id == rp_id).update(
                {"is_deleted": 1}
            )
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={
                    "message": "Role Permission Deleted Successfully.",
                    "success": True,
                },
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={
                    "message": str(e),
                    "success": False,
                },
                status_code=400,
            )


class UserPerm_DBConn:
    @staticmethod
    def getUserPData(db: Session):
        # Establishing a database connection
        try:
            data = db.query(UserPermission).filter(UserPermission.is_deleted == 0).all()
            return data  # Returning the fetched data
        except Exception as e:
            return []

    @staticmethod
    def getPermissionsOfUser(userid, db: Session):
        # Establishing a database connection
        try:
            query = text(
                """SELECT 
    bu.email AS Email, 
    r.rolename AS RoleName,
    rp.module_id AS Role_Module, 
    rp.permission_id AS Role_Permission, 
    NULL AS User_Module, 
    NULL AS User_Permission
FROM users AS bu
LEFT JOIN roles AS r ON r.id = bu.role AND r.is_deleted = 0
LEFT JOIN role_permissions AS rp ON rp.role_id = r.id AND rp.is_deleted = 0
WHERE bu.id = :idnum AND bu.is_deleted = 0

UNION ALL

SELECT 
    bu.email AS Email, 
    r.rolename AS RoleName,
    NULL AS Role_Module, 
    NULL AS Role_Permission, 
    up.module_id AS User_Module, 
    up.permission_id AS User_Permission
FROM users AS bu
LEFT JOIN roles AS r ON r.id = bu.role AND r.is_deleted = 0
LEFT JOIN user_permissions AS up ON bu.id = up.user_id AND up.is_deleted = 0
WHERE bu.id = :idnum AND bu.is_deleted = 0;"""
            )
            # result = db.execute(
            #     query, {"idnum": userid}
            # ).fetchall()  # Fetching stored procedure results

            return db.execute(
                query, {"idnum": userid}
            ).fetchall()  # Returning the permission data
        except Exception as e:
            return []

    @staticmethod
    def addUserPerm(dataList, db: Session):
        try:
            # Query to insert a new user permission record
            newUserPermission = UserPermission(
                user_id=dataList[0], module_id=dataList[1], permission_id=dataList[2]
            )
            db.add(newUserPermission)
            db.commit()  # Committing the transaction
            return True  # Returning the result

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
    def updateUserPermissionDB(recentUpdate, data2update, id, db: Session):
        try:
            # Constructing the SET clause dynamically based on columns to update
            updateData = dict(zip(recentUpdate, data2update))
            db.query(UserPermission).filter(UserPermission.id == id).update(updateData)
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={"success": True, "message": "User Permission Successfully."},
                status_code=200,
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
    def verifyPermissionsOfUser(email, db: Session):
        # Establishing a database connection
        try:
            query = text(
                """SELECT 
    bu.email AS Email, 
    r.rolename AS RoleName,
    rp.module_id AS Module_ID, 
    rp.permission_id AS Permission_ID
FROM users AS bu
JOIN roles AS r ON r.id = bu.role AND r.is_deleted = 0
JOIN role_permissions AS rp ON rp.role_id = r.id AND rp.is_deleted = 0
WHERE bu.email = :emailid AND bu.is_deleted = 0

UNION ALL

SELECT 
    bu.email AS Email, 
    r.rolename AS RoleName,
    up.module_id AS Module_ID, 
    up.permission_id AS Permission_ID
FROM users AS bu
JOIN roles AS r ON r.id = bu.role AND r.is_deleted = 0
JOIN user_permissions AS up ON bu.id = up.user_id AND up.is_deleted = 0
WHERE bu.email = :emailid AND bu.is_deleted = 0;
"""
            )
            result = db.execute(query, {"emailid": email}).fetchall()
            return result  # Returning the verification results
        except Exception as e:
            return []

    @staticmethod
    def deleteUP(up_id, db: Session):
        # Establishing a database connection
        try:
            db.query(UserPermission).filter(UserPermission.id == up_id).update(
                {"is_deleted": 1}
            )
            db.commit()  # Committing the transaction
            return True
        except Exception as e:
            return False
