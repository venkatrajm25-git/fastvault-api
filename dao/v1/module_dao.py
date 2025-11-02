from model.v1.module_model import Module
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse


class Module_DBConn:
    @staticmethod
    def getModuleData(db: Session):
        # Establishing a database connection
        modules = (
            db.query(Module).filter(Module.is_deleted == 0).all()
        )  # Query to fetch all module data
        # Fetching all results
        return modules  # Returning the fetched module data

    @staticmethod
    def addModDB(name, created_by, db: Session):
        try:
            # data = True  # Default return value indicating success
            newModule = Module(module_name=name, created_by=created_by)
            db.add(newModule)
            db.commit()  # Committing the transaction
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Module Added Successfully.",
                    "module name": name,
                },
                status_code=201,
            )
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
    def updateModuleDB(recentUpdate, data2update, module_id, db: Session):
        try:
            # Constructing the SET clause dynamically based on fields to update
            update_dict = dict(zip(recentUpdate, data2update))
            db.query(Module).filter(Module.id == module_id).update(update_dict)
            db.commit()
            return JSONResponse(
                content={"success": True, "message": "Module updated successfully."},
                status_code=200,
            )  # Returning success or duplicate status
        except IntegrityError as ie:
            db.rollback()
            # Optional: check for specific error codes
            if "1062" in str(ie.orig):
                return JSONResponse(
                    content={"success": False, "error": "Duplicate entry"},
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
    def deleteModuleDB(module_id, db: Session):
        # Establishing a database connection
        try:
            affected = (
                db.query(Module)
                .filter(Module.id == module_id)
                .update({"is_deleted": 1})
            )
            db.commit()
            return affected > 0
        except Exception as e:
            db.rollback()
            return False
