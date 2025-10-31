from model.v1.user_model import Role
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse


class Role_DBConn:
    @staticmethod
    def getRoleData(db: Session):
        # Establishing a database connection
        data = (
            db.query(Role).filter(Role.is_deleted == 0).all()
        )  # Query to fetch all roles
        return data  # Returning the fetched role data

    @staticmethod
    def createRole(dataList, db: Session):
        """Creates a new role in the database."""
        try:
            newRole = Role(
                rolename=dataList[0],
                status=dataList[1],
                created_by=dataList[2],
                is_deleted=0,  # Explicitly set is_deleted to 0 for new roles
            )
            db.add(newRole)
            db.commit()  # Commit the transaction
            return True
        except IntegrityError as ie:
            db.rollback()
            # Handle specific database errors
            error_message = str(ie.orig)
            if "1452" in error_message:  # Foreign key constraint failure
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Foreign key constraint violation",
                    },
                    status_code=400,
                )
            else:
                return JSONResponse(
                    content={"success": False, "error": "Database integrity error"},
                    status_code=400,
                )
        except Exception as e:
            db.rollback()
            return JSONResponse(
                content={
                    "success": "false",
                    "message": f"Role creation failed: {str(e)}",
                },
                status_code=400,
            )

    @staticmethod
    def updateRoleDB(id, updateRole, dataList, db: Session):
        try:
            updateRoleData = dict(zip(updateRole, dataList))
            affected_rows = db.query(Role).filter(Role.id == id).update(updateRoleData)
            db.commit()
            return affected_rows > 0  # Only return True if update was successful
        except Exception as e:
            print(f"Error updating role: {e}")
            db.rollback()
            return False
