import pytest
import json
import sqlalchemy.orm

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from model.v1.user_model import User  # Adjust import as needed
from dao.v1.user_dao import user_databaseConnection


# * REGISTER USER DETAILS STARTED
def test_register_user_details_success_with_role(db_session: Session):
    # Arrange
    # user_id, email, hashedPwd, username, status, created_by_email = user_data
    user_data = [
        999,
        "test@example.com",
        "hashed_password",
        "TestUser",
        1,
        1,
    ]
    role = 1

    # Act
    response = user_databaseConnection.registerUserDetails(user_data, role, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    response_data = json.loads(response.body.decode("utf-8"))
    print(response_data)
    assert response.status_code == 201
    assert response_data["success"] is True
    assert response_data["message"] == "User Created Successfully."

    # Verify record in DB
    user = db_session.query(User).filter(User.id == 999).first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "TestUser"
    assert user.role == 1

    # Cleanup
    db_session.query(User).filter(User.id == 999).delete()
    db_session.commit()


def test_register_user_details_success_without_role(db_session: Session):
    # Arrange
    user_data = [
        999,
        "test2@example.com",
        "hashed_password",
        "TestUser2",
        1,
        1,
    ]
    role = None

    # Act
    response = user_databaseConnection.registerUserDetails(user_data, role, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "User Created Successfully."

    # Verify record in DB
    user = db_session.query(User).filter(User.id == 999).first()
    assert user is not None
    assert user.email == "test2@example.com"
    assert user.username == "TestUser2"
    assert user.role is None

    # Cleanup
    db_session.query(User).filter(User.id == 999).delete()
    db_session.commit()


def test_register_user_details_duplicate_entry(db_session: Session):
    # Arrange: Insert a user first to trigger duplicate error
    test_user = User(
        id=999,
        email="duplicate@example.com",
        pwd="hashed_password",
        username="DuplicateUser",
        status=1,
        created_by=1,
        is_deleted=0,
    )
    db_session.add(test_user)
    db_session.commit()

    user_data = [
        999,
        "duplicate@example.com",
        "hashed_password",
        "DuplicateUser",
        1,
        1,
    ]
    role = 1

    # Act
    response = user_databaseConnection.registerUserDetails(user_data, role, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Duplicate entry"

    # Cleanup
    db_session.query(User).filter(User.id == 999).delete()
    db_session.commit()


def test_register_user_details_foreign_key_constraint(db_session: Session):
    # Arrange: Use invalid status to trigger foreign key error (assuming status has a foreign key constraint)
    user_data = [
        999,
        "test4@example.com",
        "hashed_password",
        "TestUser4",
        9999,
        1,
    ]
    role = 1

    # Act
    response = user_databaseConnection.registerUserDetails(user_data, role, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Foreign key not existed."

    # Cleanup: No cleanup needed as no record was added


def test_register_user_details_general_exception(db_session: Session):
    # Arrange: Simulate a general exception (e.g., invalid data type for user_id)
    user_data = [
        "invalid_id",
        "test5@example.com",
        "hashed_password",
        "TestUser5",
        1,
        1,
    ]
    role = "user"

    # Act
    response = user_databaseConnection.registerUserDetails(user_data, role, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert "error" in response_data

    # Cleanup: No cleanup needed as no record was added


# * REGISTER USER DETAILS ENDED


# * GET USER TABLE STARTED
def test_get_user_table_success(db_session: Session):
    # Arrange: Insert a test user if none exist
    data = db_session.query(User).filter(User.is_deleted == 0).first()
    if not data:
        test_user = User(
            id=999,
            email="test6@example.com",
            pwd="hashed_password",
            username="TestUser6",
            status=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

    # Act
    result = user_databaseConnection.getUserTable(db_session)

    # Assert
    assert isinstance(result, list), "Result should be a list"
    assert len(result) >= 1, "Result should contain at least one record"

    # Cleanup
    if not data:  # Only clean up if we inserted a test user
        db_session.query(User).filter(User.id == 999).delete()
        db_session.commit()


def test_get_user_table_exception(db_session: Session, monkeypatch):
    # Arrange: Simulate a database connection error
    def mock_query(*args, **kwargs):
        raise Exception("Simulated DB error")

    monkeypatch.setattr(db_session, "query", mock_query)

    # Act
    response = user_databaseConnection.getUserTable(db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Database Connection Error."

    # Cleanup: None needed


# * GET USER TABLE ENDED


# * UPDATE USER STARTED
def test_update_user_success(db_session: Session):
    data = db_session.query(User).filter(User.id == 999, User.is_deleted == 0).first()
    if not data:
        test_user = User(
            id=999,
            email="test6@example.com",
            pwd="hashed_password",
            username="TestUser6",
            status=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

    update_fields = ["username", "status"]
    update_data = ["UpdatedUser7", 2]

    # Act
    result = user_databaseConnection.updateUser(
        test_user.id, update_fields, update_data, db_session
    )

    # Assert
    assert result is True, "Update should return True"

    # Verify updated record in DB
    updated_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert updated_user is not None
    assert updated_user.username == "UpdatedUser7"
    assert updated_user.status == 2

    # Cleanup
    db_session.query(User).filter(User.id == test_user.id).delete()
    db_session.commit()


def test_update_user_non_existent(db_session: Session):
    # Arrange
    update_fields = ["username", "status"]
    update_data = ["UpdatedUser", 2]
    non_existent_id = 9999

    # Act
    result = user_databaseConnection.updateUser(
        non_existent_id, update_fields, update_data, db_session
    )

    # Assert
    assert result is False, "Update on non-existent user should return False"

    # Cleanup: None needed


def test_update_user_exception(db_session: Session):
    # Arrange: Insert a test user
    data = db_session.query(User).filter(User.id == 999).first()
    if not data:
        test_user = User(
            id=999,
            email="test8@example.com",
            pwd="hashed_password",
            username="TestUser8",
            status=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(test_user)
        db_session.commit()

    # Use invalid data to trigger exception (e.g., invalid status value for foreign key)
    update_fields = ["status"]
    update_data = [9999]  # Assuming status has a foreign key constraint

    # Act
    result = user_databaseConnection.updateUser(
        test_user.id, update_fields, update_data, db_session
    )

    # Assert
    assert result is False, "Update with invalid data should return False"

    # Cleanup
    db_session.query(User).filter(User.id == test_user.id).delete()
    db_session.commit()


# * UPDATE USER ENDED


# * DELETE USER STARTED
def test_delete_user_success(db_session: Session):
    data = db_session.query(User).filter(User.id == 999).first()
    if not data:
        test_user = User(
            id=999,
            email="test8@example.com",
            pwd="hashed_password",
            username="TestUser8",
            status=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(test_user)
        db_session.commit()

        db_session.refresh(test_user)

    # Act
    result = user_databaseConnection.deleteUserDB(test_user.id, db_session)

    # Assert
    assert result is True, "Delete should return True"

    # Verify user is soft-deleted
    deleted_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert deleted_user is not None
    assert deleted_user.is_deleted == 1

    # Cleanup
    db_session.query(User).filter(User.id == test_user.id).delete()
    db_session.commit()


def test_delete_user_non_existent(db_session: Session):
    # Arrange
    non_existent_id = 9999

    # Act
    result = user_databaseConnection.deleteUserDB(non_existent_id, db_session)

    # Assert
    assert result is False, "Delete on non-existent user should return False"

    # Cleanup: None needed


def test_delete_user_exception(db_session: Session, monkeypatch):
    # Arrange: Simulate a database error
    def mock_update(*args, **kwargs):
        raise Exception("Simulated DB error")

    # Patch the update method of the Query object
    monkeypatch.setattr(sqlalchemy.orm.Query, "update", mock_update)

    # Act
    result = user_databaseConnection.deleteUserDB(999, db_session)

    # Assert
    assert result is False, "Delete with DB error should return False"

    # Cleanup: None needed


# * DELETE USER ENDED
