from urllib import response
import pytest
from sqlalchemy.orm import Session
from model.v1.user_model import Role  # Adjust import as needed
from dao.v1.role_dao import Role_DBConn
from fastapi.responses import JSONResponse
import json
from unittest.mock import MagicMock
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


# Test for getRoleData
def test_get_role_data_success(db_session: Session):
    # Arrange: Insert a test Role record
    test_role = Role(role_name="Test Role", status=1, created_by=999, is_deleted=0)
    db_session.add(test_role)
    db_session.commit()
    db_session.refresh(test_role)

    # Act
    result = Role_DBConn.getRoleData(db_session)

    # Assert
    assert isinstance(result, list), "Result should be a list"
    assert len(result) >= 1, "Result should contain at least one record"
    assert any(
        r.role_name == "Test Role" for r in result
    ), "Result should contain 'Test Role'"

    # Cleanup
    db_session.query(Role).filter(Role.id == test_role.id).delete()
    db_session.commit()


# Test for createRole (success case)
def test_create_role_success(db_session: Session):
    # Arrange
    test_data = ["New Role", 1, 999]  # role_name, status, created_by

    # Act
    result = Role_DBConn.createRole(test_data, db_session)

    # Assert
    assert result is True, "Role creation should return True"

    # Verify record in DB
    added_role = db_session.query(Role).filter(Role.role_name == "New Role").first()
    assert added_role is not None, "Role should exist in database"
    assert added_role.role_name == "New Role", "Role name should match"
    assert added_role.status == 1, "Status should match"
    assert added_role.created_by == 999, "Created_by should match"

    # Cleanup
    db_session.query(Role).filter(Role.id == added_role.id).delete()
    db_session.commit()


def test_create_role_duplicate_entry(db_session: Session):
    # Arrange: Insert a Role first
    data = db_session.query(Role).filter(Role.role_name == "Duplicate Role").first()
    if not data:
        test_role = Role(
            role_name="Duplicate Role", status=1, created_by=1, is_deleted=0
        )
        db_session.add(test_role)
        db_session.commit()

    test_data = ["Duplicate Role", 1, 1]  # Same role_name to trigger duplicate error

    # Act
    response = Role_DBConn.createRole(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400

    result = json.loads(response.body.decode("utf-8"))
    assert result["success"] is False

    # Cleanup
    db_session.query(Role).filter(Role.role_name == "Duplicate Role").delete()
    db_session.commit()


def test_create_role_foreign_key_contraint(db_session: Session):

    test_data = ["Duplicate Role", 500, 1]  # status - foreign key failure

    # Act
    response = Role_DBConn.createRole(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False


class FakeOrig(Exception):
    def __str__(self):
        return "1452 Cannot add or update a child row: a foreign key constraint fails"


def test_create_role_integrity_error_foreign_key():
    db = MagicMock()
    # Create fake orig with a message that includes '1452'
    fake_orig = FakeOrig()
    db.add.side_effect = IntegrityError("Integrity Error", None, fake_orig)

    response = Role_DBConn.createRole(["role1", 50, 99999], db)

    assert isinstance(response, JSONResponse)
    print(response.body)
    assert response.status_code == 400


def test_create_role_integrity_error_general():
    db = MagicMock()
    # Simulate general IntegrityError
    db.add.side_effect = IntegrityError("General integrity error", None, None)

    response = Role_DBConn.createRole(["role1", "active", 1], db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400


# Test for updateRoleDB (success case)
def test_update_role_success(db_session: Session):
    # Arrange: Insert a test Role record
    test_role = Role(role_name="Old Role", status=1, created_by=999, is_deleted=0)
    db_session.add(test_role)
    db_session.commit()
    db_session.refresh(test_role)

    update_fields = ["role_name", "status"]  # Fields to update
    update_data = ["Updated Role", 2]  # New values

    # Act
    result = Role_DBConn.updateRoleDB(
        test_role.id, update_fields, update_data, db_session
    )

    # Assert
    assert result is True, "Role update should return True"

    # Verify updated record in DB
    updated_role = db_session.query(Role).filter(Role.id == test_role.id).first()
    assert updated_role is not None, "Updated role should exist"
    assert updated_role.role_name == "Updated Role", "Role name should be updated"
    assert updated_role.status == 2, "Status should be updated"

    # Cleanup
    db_session.query(Role).filter(Role.id == test_role.id).delete()
    db_session.commit()


# Test for updateRoleDB (non-existent role)
def test_update_role_non_existent(db_session: Session):
    # Arrange
    update_fields = ["role_name", "status"]
    update_data = ["Updated Role", 2]
    non_existent_id = 9999  # Assume this ID does not exist

    # Act
    result = Role_DBConn.updateRoleDB(
        non_existent_id, update_fields, update_data, db_session
    )

    # Assert
    assert result is False, "Update on non-existent role should return False"

    # No cleanup needed since no data was modified


def test_update_role_general_exception():
    db = MagicMock()
    # Simulate unexpected general exception
    db.query().filter().update.side_effect = Exception("Unexpected crash")

    response = Role_DBConn.updateRoleDB(1, ["role_name"], ["new_role"], db)

    assert response is False
