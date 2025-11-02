import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from dao.v1.module_dao import Module_DBConn
from dao.v1.perm_dao import Permissions_DBConn, RolePerm_DBConn, UserPerm_DBConn
from model.v1.permission_model import Permission, RolePermission, UserPermission


# Mock translation functions for RolePerm_DBConn
def mock_translate(key, lang=None):
    return key


def mock_translate_many(keys, lang=None):
    return " ".join(keys)


def mock_translate_pair(key, value, lang=None):
    return {key: value}


# * GET PERMISSION DATA STARTED
def test_get_permission_data_success(db_session):
    """Test successful retrieval of permission data"""
    # Arrange: add temporary permission records
    perm_1 = Permission(name="perm1", created_by=1, is_deleted=0)
    perm_2 = Permission(name="perm2", created_by=1, is_deleted=0)
    db_session.add_all([perm_1, perm_2])
    db_session.commit()
    perm_ids = [perm_1.id, perm_2.id]

    # Act
    result = Permissions_DBConn.getPermissionData(db_session)

    # Assert
    assert isinstance(result, list)
    assert len(result) >= 2
    assert any(p.name == "perm1" for p in result)
    assert any(p.name == "perm2" for p in result)

    # Cleanup
    db_session.query(Permission).filter(Permission.id.in_(perm_ids)).delete(
        synchronize_session=False
    )
    db_session.commit()


# * GET PERMISSION DATA ENDED


# * ADD PERMISSION DB STARTED
def test_add_permission_db_success(db_session):
    """Test successful addition of a permission"""
    # Arrange
    name = "Testing_Permission"
    created_by = 1
    data = db_session.query(Permission).filter(Permission.name == name).first()
    if data:
        db_session.query(Permission).filter(Permission.name == name).delete()

    # Act
    response = Permissions_DBConn.addPermissionDB(name, created_by, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_201_CREATED
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Permission added"

    # Verify database
    perm = db_session.query(Permission).filter_by(name=name).first()
    assert perm is not None
    assert perm.created_by == created_by
    assert perm.is_deleted == 0

    # Cleanup
    db_session.query(Permission).filter_by(id=perm.id).delete()
    db_session.commit()


def test_add_permission_db_duplicate_entry(db_session):
    """Test adding a permission with duplicate name"""

    name = "test_permission"
    user_id = 1

    # Ensure test_permission exists
    existing = db_session.query(Permission).filter_by(name=name, is_deleted=0).first()
    if not existing:
        existing = Permission(name=name, created_by=user_id, is_deleted=0)
        db_session.add(existing)
        db_session.commit()
        db_session.refresh(existing)

    # Prepare a duplicate entry
    duplicate_permission = Permission(name=name, created_by=user_id, is_deleted=0)
    db_session.add(duplicate_permission)

    # Mock the commit to raise IntegrityError on duplicate
    with patch.object(db_session, "commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(
            statement="INSERT INTO permission ...",
            params={},
            orig=Exception(
                "1062 Duplicate entry 'test_permission' for key 'permission.name'"
            ),
        )
        response = Permissions_DBConn.addPermissionDB(name, user_id, db_session)

        # Validate response
        assert isinstance(response, JSONResponse)
        assert response.status_code == HTTP_400_BAD_REQUEST
        response_data = json.loads(response.body.decode("utf-8"))
        assert response_data["success"] is False
        assert response_data["error"] == "Duplicate entry"

    # Cleanup only the uncommitted duplicate (safe guard if any commit went through)
    db_session.rollback()


def test_add_permission_other_integrity_error():
    db = MagicMock()
    db.add.side_effect = IntegrityError(
        statement=None,
        params=None,
        orig=Exception("1452 Cannot add or update a child row"),
    )

    response = Permissions_DBConn.addPermissionDB(
        name="Invalid Foreign Key", created_by=999, db=db
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'
    db.rollback.assert_called_once()


def test_add_permission_db_general_exception(db_session):
    """Test adding a permission with general exception"""
    # Arrange
    name = "test_permission"
    user_id = 1

    # Mock general exception
    with patch("sqlalchemy.orm.Session.commit", side_effect=Exception("Test error")):
        # Act
        response = Permissions_DBConn.addPermissionDB(name, user_id, db_session)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == HTTP_400_BAD_REQUEST
        response_data = json.loads(response.body.decode("utf-8"))
        assert response_data["success"] is False
        assert response_data["error"] == "Test error"


# * ADD PERMISSION DB ENDED


# * UPDATE PERMISSION DB STARTED
def test_update_permission_db_success(db_session):
    """Test successful update of a permission"""

    existing = (
        db_session.query(Permission).filter_by(name="old_name", is_deleted=0).first()
    )

    if not existing:
        perm = Permission(name="old_name", created_by=1, is_deleted=0)
        db_session.add(perm)
        db_session.commit()
        perm_id = perm.id
    else:
        perm_id = existing.id

    current = db_session.query(Permission).filter_by(id=perm_id).first()
    assert current is not None
    assert current.name == "old_name"

    recent_update = ["name"]
    data2update = ["new_name"]

    response = Permissions_DBConn.updatePermissionDB(
        recent_update, data2update, perm_id, db_session
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_200_OK
    res_data = json.loads(response.body.decode("utf-8"))
    assert res_data["success"] is True
    assert res_data["message"] == "Permission updated successfully."

    updated = db_session.query(Permission).filter_by(id=perm_id).first()
    assert updated.name == "new_name"

    db_session.query(Permission).filter_by(id=perm_id).delete()
    db_session.commit()


def test_update_permission_db_duplicate_entry(db_session):
    """Test updating a permission with duplicate name"""

    existing_1 = (
        db_session.query(Permission).filter_by(name="old_name", is_deleted=0).first()
    )
    if not existing_1:
        perm = Permission(name="old_name", created_by=1, is_deleted=0)
        db_session.add(perm)
        db_session.commit()
        perm_id = perm.id
    else:
        perm_id = existing_1.id

    existing_2 = (
        db_session.query(Permission)
        .filter_by(name="existing_name", is_deleted=0)
        .first()
    )
    if not existing_2:
        perm2 = Permission(name="existing_name", created_by=1, is_deleted=0)
        db_session.add(perm2)
        db_session.commit()
        perm2_id = perm2.id
    else:
        perm2_id = existing_2.id

    recent_update = ["name"]
    data2update = ["existing_name"]

    response = Permissions_DBConn.updatePermissionDB(
        recent_update, data2update, perm_id, db_session
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Duplicate entry"

    db_session.query(Permission).filter(Permission.id == perm_id).delete()
    db_session.query(Permission).filter(Permission.id == perm2_id).delete()
    db_session.commit()


def test_update_permission_db_foreign_key_error(db_session):
    """Test updating a permission with invalid foreign key"""
    # Arrange
    existing_1 = (
        db_session.query(Permission).filter_by(name="old_name", is_deleted=0).first()
    )
    if not existing_1:
        perm = Permission(name="old_name", created_by=1, is_deleted=0)
        db_session.add(perm)
        db_session.commit()
        perm_id = perm.id
    else:
        perm_id = existing_1.id

    existing_2 = (
        db_session.query(Permission)
        .filter_by(name="existing_name", is_deleted=0)
        .first()
    )
    if not existing_2:
        perm2 = Permission(name="existing_name", created_by=1, is_deleted=0)
        db_session.add(perm2)
        db_session.commit()
        perm2_id = perm2.id
    else:
        perm2_id = existing_2.id

    recent_update = ["created_by"]
    data2update = [9999]  # Invalid foreign key

    # # Mock IntegrityError for foreign key violation
    # with patch(
    #     "sqlalchemy.orm.Session.commit",
    #     side_effect=IntegrityError("1452", "Foreign key constraint fails", None),
    # ):
    #     # Act
    response = Permissions_DBConn.updatePermissionDB(
        recent_update, data2update, perm_id, db_session
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Foreign key not existed."

    db_session.query(Permission).filter(Permission.id == perm_id).delete()
    db_session.query(Permission).filter(Permission.id == perm2_id).delete()
    db_session.commit()


def test_update_permission_integrity_generic_error():
    db = MagicMock()
    db.commit.side_effect = IntegrityError(
        statement=None, params=None, orig=Exception("Some other DB integrity error")
    )

    response = Permissions_DBConn.updatePermissionDB(
        recentUpdate=["name"],
        data2update=["invalid_data"],
        permission_id=1,
        db=db,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'


def test_update_permission_general_exception():
    db = MagicMock()

    # Simulate a failure in `.update()` itself, not just commit
    db.query.return_value.filter.return_value.update.side_effect = Exception(
        "Unexpected error"
    )

    response = Permissions_DBConn.updatePermissionDB(
        recentUpdate=["name"],
        data2update=["something_bad"],
        permission_id=1,
        db=db,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Unexpected error"}'


# * UPDATE PERMISSION DB ENDED


# * DELETE PERMISSION DB STARTED
def test_delete_permission_db_success(db_session):
    """Test successful soft deletion of a permission"""
    # Arrange
    data = (
        db_session.query(Permission)
        .filter(Permission.name == "test_permission")
        .first()
    )
    if not data:
        data = Permission(name="test_permission", created_by=1, is_deleted=0)
        db_session.add(data)
        db_session.commit()
        db_session.refresh(data)

    perm_id = data.id

    # Act
    result = Permissions_DBConn.deletePermissionDB(perm_id, db_session)

    # Assert
    assert result is True
    updated_perm = db_session.query(Permission).filter_by(id=perm_id).first()
    assert updated_perm.is_deleted == 1

    # Cleanup
    db_session.query(Permission).filter_by(id=perm_id).delete()
    db_session.commit()


def test_delete_permission_db_exception(db_session):
    """Test soft deletion with exception"""
    # Arrange
    perm = Permission(name="test_permission", created_by=1, is_deleted=0)
    db_session.add(perm)
    db_session.commit()
    perm_id = perm.id

    # Mock exception
    with patch("sqlalchemy.orm.Session.commit", side_effect=Exception("Test error")):
        # Act
        result = Permissions_DBConn.deletePermissionDB(perm_id, db_session)

        # Assert
        assert result == "Error"

    # Cleanup
    db_session.query(Permission).filter_by(id=perm_id).delete()
    db_session.commit()


# * DELETE PERMISSION DB ENDED


# * GET RP DATA STARTED
def test_get_rp_data_success(db_session):
    """Test successful retrieval of role permission data"""

    # Arrange
    def add_or_restore_if_needed(role_id, module_id, permission_id):
        existing = (
            db_session.query(RolePermission)
            .filter_by(
                role_id=role_id, module_id=module_id, permission_id=permission_id
            )
            .first()
        )
        if existing:
            if existing.is_deleted == 1:
                existing.is_deleted = 0
                db_session.commit()
            return existing.id
        else:
            rp = RolePermission(
                role_id=role_id,
                module_id=module_id,
                permission_id=permission_id,
                is_deleted=0,
            )
            db_session.add(rp)
            db_session.commit()
            return rp.id

    rp_id_1 = add_or_restore_if_needed(1, 1, 1)
    rp_id_2 = add_or_restore_if_needed(2, 2, 2)
    rp_ids = [rp_id_1, rp_id_2]

    # Act
    result = RolePerm_DBConn.getRPData(db_session)

    # Assert
    assert isinstance(result, list)
    assert any(rp.role_id == 1 for rp in result)
    assert any(rp.role_id == 2 for rp in result)

    # Cleanup (optional)
    db_session.query(RolePermission).filter(RolePermission.id.in_(rp_ids)).update(
        {"is_deleted": 1}, synchronize_session=False
    )
    db_session.commit()


def test_get_rp_data_exception(db_session):
    """Test retrieval of role permission data with exception"""
    # Mock exception
    with patch("sqlalchemy.orm.Session.query", side_effect=Exception("Test error")):
        # Act
        result = RolePerm_DBConn.getRPData(db_session)

        # Assert
        assert result == []


# * GET RP DATA ENDED


# * ADD ROLE PERM STARTED
def test_add_role_perm_success(db_session):
    """Test successful addition of a role permission"""
    # Arrange
    db_session.query(RolePermission).filter_by(
        role_id=1, module_id=1, permission_id=1
    ).delete()
    db_session.commit()

    data_list = [1, 1, 1]  # role_id, module_id, permission_id
    accept_language = "en"

    # Act
    response = RolePerm_DBConn.addRolePerm(data_list, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    response_data = json.loads(response.body.decode("utf-8"))
    print(response_data)
    assert response.status_code == HTTP_201_CREATED
    assert response_data["success"] == "true"
    assert response_data["message"] == "Role Permission Added Successfully."

    # Verify database
    rp = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )
    assert rp is not None
    assert rp.is_deleted == 0

    # Cleanup
    db_session.query(RolePermission).filter_by(id=rp.id).delete()
    db_session.commit()


def test_add_role_perm_duplicate_entry(db_session):
    """Test adding a role permission with duplicate entry"""
    # Arrange
    data_list = [1, 1, 1]
    accept_language = "en"
    rp = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )
    if not rp:
        rp = RolePermission(role_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(rp)
        db_session.commit()

        # Act
    response = RolePerm_DBConn.addRolePerm(data_list, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Duplicate entry"

    # Cleanup
    db_session.query(RolePermission).filter_by(id=rp.id).delete()
    db_session.commit()


def test_add_role_permission_generic_integrity_error():
    db = MagicMock()

    # Simulate a different kind of IntegrityError
    integrity_error = IntegrityError(
        "Some constraint failed", params=None, orig=Exception("Something else")
    )
    db.commit.side_effect = integrity_error

    response = RolePerm_DBConn.addRolePerm([1, 2, 3], db="en")

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'


def test_add_role_permission_general_exception():
    db = MagicMock()

    # Simulate unexpected error on db.add()
    db.add.side_effect = Exception("Unexpected crash")

    response = RolePerm_DBConn.addRolePerm([1, 2, 3], db="en")

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Unexpected crash"}'


# * ADD ROLE PERM ENDED


def test_update_role_permission_db_success(db_session):
    """Test successful update of a role permission using updateRolePermissionDB"""

    # Arrange - ensure a known state
    rp = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )
    if not rp:
        rp = RolePermission(role_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(rp)
        db_session.commit()

    rp_id = rp.id
    recent_update = ["role_id", "module_id"]
    data2update = [2, 2]
    accept_language = "en"

    # Act
    response = RolePerm_DBConn.updateRolePermissionDB(
        recent_update, data2update, rp_id, db_session
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_201_CREATED

    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] == "true"
    assert response_data["message"] == "Role Permission Updated Successfully"
    assert response_data["updated_fields"] == {"role_id": 2, "module_id": 2}

    # DB Check
    updated_rp = db_session.query(RolePermission).filter_by(id=rp_id).first()
    assert updated_rp.role_id == 2
    assert updated_rp.module_id == 2

    # Cleanup
    db_session.delete(updated_rp)
    db_session.commit()


def test_update_role_permission_db_duplicate_entry(db_session):
    """Test updating a role permission where the update causes a duplicate entry"""

    # Ensure first record (1,1,1) exists
    rp1 = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )
    if not rp1:
        rp1 = RolePermission(role_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(rp1)
        db_session.commit()

    # Ensure second record (2,2,2) exists
    rp2 = (
        db_session.query(RolePermission)
        .filter_by(role_id=2, module_id=2, permission_id=2)
        .first()
    )
    if not rp2:
        rp2 = RolePermission(role_id=2, module_id=2, permission_id=2, is_deleted=0)
        db_session.add(rp2)
        db_session.commit()

    rp1_id = rp1.id
    # Now, try updating rp1 to match rp2, which should cause a duplicate
    recent_update = ["role_id", "module_id", "permission_id"]
    data2update = [2, 2, 2]
    accept_language = "en"

    response = RolePerm_DBConn.updateRolePermissionDB(
        recent_update, data2update, rp1_id, db_session
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] == "false"
    assert response_data["message"] == "Role Permission Already exists."

    # Cleanup: optional, if you want to clean test data
    db_session.query(RolePermission).filter(RolePermission.id == rp1_id).delete()
    db_session.query(RolePermission).filter(RolePermission.id == rp2.id).delete()
    db_session.commit()


def test_update_role_permission_foreign_key_error():
    # Arrange
    db = MagicMock()
    db.query().filter().update.side_effect = None
    db.commit.side_effect = IntegrityError(
        "1452 Cannot add or update", orig="1452", params=None
    )

    # Act
    response = RolePerm_DBConn.updateRolePermissionDB(
        ["permission_id"], [999], 10, db, "en"
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body.decode() == '{"error":"Foreign key not existed."}'


def test_update_role_permission_other_integrity_error():
    # Arrange
    db = MagicMock()
    db.query().filter().update.side_effect = None
    db.commit.side_effect = IntegrityError("Random DB error", orig="1234", params=None)

    # Act
    response = RolePerm_DBConn.updateRolePermissionDB(["role_id"], [2], 8, db, "en")

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body.decode() == '{"error":"Database integrity error"}'


def test_update_role_permission_general_exception():
    db = MagicMock()
    # Simulate unexpected general exception
    db.query().filter().update.side_effect = Exception("Unexpected crash")

    response = RolePerm_DBConn.updateRolePermissionDB(
        ["field1"], ["value1"], 1, db="en"
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":"false","message":"Unexpected crash"}'


# * UPDATE ROLE PERMISSION DB ENDED


# * DELETE RP STARTED
def test_delete_rp_success(db_session):
    """Test successful soft deletion of a role permission"""

    # Ensure the record (1,1,1) exists
    rp = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )
    if not rp:
        rp = RolePermission(role_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(rp)
        db_session.commit()

    rp_id = rp.id

    # Act
    response = RolePerm_DBConn.deleteRp(rp_id, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_200_OK
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Role Permission Deleted Successfully."

    # Verify soft delete
    updated_rp = db_session.query(RolePermission).filter_by(id=rp_id).first()
    assert updated_rp.is_deleted == 1

    # Cleanup: Revert is_deleted back to 0 (instead of deleting the record)
    db_session.query(RolePermission).filter_by(id=rp_id).update({"is_deleted": 0})
    db_session.commit()


def test_delete_rp_exception(db_session):
    """Test soft deletion of a role permission with exception"""

    # Ensure the (1,1,1) RolePermission exists
    existing_rp = (
        db_session.query(RolePermission)
        .filter_by(role_id=1, module_id=1, permission_id=1)
        .first()
    )

    if not existing_rp:
        rp = RolePermission(role_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(rp)
        db_session.commit()
        rp_id = rp.id
    else:
        # Use existing one
        rp_id = existing_rp.id
        # Reset is_deleted to 0 if needed
        if existing_rp.is_deleted:
            existing_rp.is_deleted = 0
            db_session.commit()

    # Mock commit exception
    with patch("sqlalchemy.orm.Session.commit", side_effect=Exception("Test error")):
        # Act
        response = RolePerm_DBConn.deleteRp(rp_id, db_session)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == HTTP_400_BAD_REQUEST
        response_data = json.loads(response.body.decode("utf-8"))
        assert response_data["success"] is False
        assert response_data["message"] == "Test error"

    # Cleanup: Set is_deleted = 0 back if modified
    rp_obj = db_session.query(RolePermission).filter_by(id=rp_id).first()
    if rp_obj and rp_obj.is_deleted:
        rp_obj.is_deleted = 0
        db_session.commit()


# * DELETE RP ENDED


# * GET USER P DATA STARTED
def test_get_user_permission_data_success(db_session):
    """Test successful retrieval of user permission data"""
    # Arrange
    db_session.query(UserPermission).filter_by(
        user_id=1, module_id=1, permission_id=1
    ).delete()
    db_session.query(UserPermission).filter_by(
        user_id=2, module_id=2, permission_id=2
    ).delete()

    up_1 = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
    up_2 = UserPermission(user_id=2, module_id=2, permission_id=2, is_deleted=0)
    db_session.add_all([up_1, up_2])
    db_session.commit()
    up_ids = [up_1.id, up_2.id]

    # Act
    result = UserPerm_DBConn.getUserPData(db_session)

    # Assert
    assert isinstance(result, list)
    assert len(result) >= 2
    assert any(up.user_id == 1 for up in result)
    assert any(up.user_id == 2 for up in result)

    # Cleanup
    db_session.query(UserPermission).filter(UserPermission.id.in_(up_ids)).delete(
        synchronize_session=False
    )
    db_session.commit()


def test_get_user_permission_data_exception(db_session):
    """Test retrieval of user permission data with exception"""
    # Mock exception
    with patch("sqlalchemy.orm.Session.query", side_effect=Exception("Test error")):
        # Act
        result = UserPerm_DBConn.getUserPData(db_session)

        # Assert
        assert result == []


# * GET USER PERMISSION DATA ENDED


# * GET PERMISSIONS OF USER STARTED
def test_get_permissions_of_user_success(db_session):
    """Test successful retrieval of user permissions"""
    mock_result = [
        ("test@jeenox.com", "Admin", 1, 1, None, None),
        ("test@jeenox.com", "Admin", None, None, 2, 2),
    ]
    with patch.object(db_session, "execute", return_value=mock_result) as mock_execute:
        result = UserPerm_DBConn.getPermissionsOfUser(userid=1, db=db_session)

        assert isinstance(result, list)


def test_get_permissions_of_user_exception(db_session):
    """Test retrieval of user permissions with exception"""
    # Mock exception
    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("Test error")):
        # Act
        result = UserPerm_DBConn.getPermissionsOfUser(userid=1, db=db_session)

        # Assert
        assert result == []


# * GET PERMISSIONS OF USER ENDED


# * ADD USER PERM STARTED
def test_add_user_perm_success(db_session):
    """Test successful addition of a user permission"""
    # Arrange
    data_list = [1, 1, 1]  # user_id, module_id, permission_id

    # Act
    result = UserPerm_DBConn.addUserPerm(data_list, db_session)

    # Assert
    assert result is True
    up = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1)
        .first()
    )
    assert up is not None
    assert up.is_deleted == 0

    # Cleanup
    db_session.query(UserPermission).filter_by(id=up.id).delete()
    db_session.commit()


def test_add_user_perm_duplicate_entry(db_session):
    """Test adding a user permission with duplicate entry (should not allow)"""
    # Arrange
    data_list = [1, 1, 1]  # user_id, module_id, permission_id

    # Step 1: Check if entry exists, if not, add it first
    existing = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )

    if not existing:
        new_perm = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(new_perm)
        db_session.commit()

    # Step 2: Try adding again, which should fail due to unique constraint
    response = UserPerm_DBConn.addUserPerm(data_list, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert "Duplicate entry" in response_data["error"]


def test_add_user_perm_foreign_key_error(db_session):
    """Test adding a user permission with invalid foreign key"""
    # Arrange
    data_list = [9999, 1, 1]  # Invalid user_id

    # Mock IntegrityError for foreign key violation
    # Act
    response = UserPerm_DBConn.addUserPerm(data_list, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "Foreign key not existed."


def test_add_user_permission_integrity_error_general():
    db = MagicMock()
    # Simulate general IntegrityError
    db.add.side_effect = IntegrityError("General integrity error", None, None)

    response = UserPerm_DBConn.addUserPerm([1, 2, 3], db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'


def test_add_user_permission_general_exception():
    db = MagicMock()
    # Simulate unexpected general exception
    db.add.side_effect = Exception("Unexpected crash")

    response = UserPerm_DBConn.addUserPerm([1, 2, 3], db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Unexpected crash"}'


# * ADD USER PERM ENDED


# * UPDATE USER PERMISSION DB STARTED
def test_update_user_permission_db_success(db_session):
    """Test successful update of a user permission"""

    # === Step 1: Ensure clean starting state ===
    # Check if (1,1,1) exists
    existing_111 = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )

    # If not, add (1,1,1)
    if not existing_111:
        up = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(up)
        db_session.commit()
        up_id = up.id
        added_new = True
    else:
        up_id = existing_111.id
        added_new = False

    # === Step 2: Verify target update (1,2,2) doesn't already exist ===
    conflict_check = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=2, permission_id=2, is_deleted=0)
        .first()
    )
    if conflict_check:
        # Remove temporarily to avoid integrity error
        db_session.delete(conflict_check)
        db_session.commit()
        deleted_conflict = True
    else:
        deleted_conflict = False

    # === Step 3: Actual test ===
    recent_update = ["module_id", "permission_id"]
    data2update = [2, 2]

    response = UserPerm_DBConn.updateUserPermissionDB(
        recent_update, data2update, up_id, db_session
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_200_OK
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "User Permission Successfully."

    updated_up = db_session.query(UserPermission).filter_by(id=up_id).first()
    assert updated_up.module_id == 2
    assert updated_up.permission_id == 2

    # === Step 4: Revert back ===
    if added_new:
        db_session.delete(updated_up)
    else:
        updated_up.module_id = 1
        updated_up.permission_id = 1
    db_session.commit()

    # === Step 5: Restore deleted conflict if any ===
    if deleted_conflict:
        db_session.add(
            UserPermission(user_id=1, module_id=2, permission_id=2, is_deleted=0)
        )
        db_session.commit()


def test_update_user_permission_db_duplicate_entry(db_session):
    """Test updating a user permission with duplicate entry"""
    # --- VERIFY & ARRANGE ---

    # Ensure (1,1,1) exists
    up1 = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )
    if not up1:
        up1 = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(up1)
        db_session.commit()
    up1_id = up1.id

    # Ensure (1,2,2) exists (target of update to cause duplicate)
    up2 = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=2, permission_id=2, is_deleted=0)
        .first()
    )
    if not up2:
        up2 = UserPermission(user_id=1, module_id=2, permission_id=2, is_deleted=0)
        db_session.add(up2)
        db_session.commit()
    up2_id = up2.id

    # --- ACT (simulate duplicate update) ---
    recent_update = ["module_id", "permission_id"]
    data2update = [2, 2]  # Intentionally trying to make it a duplicate

    with patch(
        "sqlalchemy.orm.Session.commit",
        side_effect=IntegrityError("1062", "Duplicate entry", None),
    ):
        response = UserPerm_DBConn.updateUserPermissionDB(
            recent_update, data2update, up1_id, db_session
        )

    # --- ASSERT ---
    assert isinstance(response, JSONResponse)
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Duplicate entry"

    # --- CLEANUP / REVERT ---

    # If we added (1,1,1), don't delete it. Just ensure original state.
    original_up = db_session.query(UserPermission).filter_by(id=up1_id).first()
    if original_up:
        original_up.module_id = 1
        original_up.permission_id = 1
        db_session.commit()

    # If we added (1,2,2), remove it
    if not up2_id:
        db_session.query(UserPermission).filter_by(
            user_id=1, module_id=2, permission_id=2, is_deleted=0
        ).delete()
        db_session.commit()


def test_update_user_permission_foreign_key_contraint_error():
    db = MagicMock()

    # Create a mock orig object with '1452' in its string representation
    class MockOrig:
        def __str__(self):
            return "(_mysql_exceptions.IntegrityError) 1452: Cannot add or update a child row: a foreign key constraint fails"

    # Raise IntegrityError with mocked orig
    db.query().filter().update.side_effect = IntegrityError(
        statement=None, params=None, orig=MockOrig()
    )

    # from your_module import UserPerm_DBConn  # Replace with your actual import

    response = UserPerm_DBConn.updateUserPermissionDB(["field1"], ["value1"], 1, db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Foreign key not existed."}'


def test_update_user_permission_integrity_error_general():
    db = MagicMock()
    # Simulate general IntegrityError
    db.query().filter().update.side_effect = IntegrityError(
        "General integrity error", None, None
    )

    response = UserPerm_DBConn.updateUserPermissionDB(["field1"], ["value1"], 1, db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'


def test_update_user_permission_general_exception():
    db = MagicMock()
    # Simulate unexpected general exception
    db.query().filter().update.side_effect = Exception("Unexpected crash")

    response = UserPerm_DBConn.updateUserPermissionDB(["field1"], ["value1"], 1, db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Unexpected crash"}'


# * UPDATE USER PERMISSION DB ENDED


# * VERIFY PERMISSIONS OF USER STARTED
def test_verify_permissions_of_user_success(db_session):
    """Test successful verification of user permissions"""
    # Arrange: Mock SQL query result
    mock_result = [(["test@jeenox.com", 1, 1, 1]), (["test@jeenox.com", 1, 2, 2])]
    with patch(
        "sqlalchemy.orm.Session.execute", return_value=mock_result
    ) as mock_execute:
        # Act
        result = UserPerm_DBConn.verifyPermissionsOfUser(
            email="test@jeenox.com", db=db_session
        )

        # Assert
        assert isinstance(result, list)


def test_verify_permissions_of_user_exception(db_session):
    """Test verification of user permissions with exception"""
    # Mock exception
    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("Test error")):
        # Act
        result = UserPerm_DBConn.verifyPermissionsOfUser(
            email="test@jeenox.com", db=db_session
        )

        # Assert
        assert result == []


# * VERIFY PERMISSIONS OF USER ENDED


# * DELETE UP STARTED
def test_delete_up_success(db_session):
    """Test successful soft deletion of a user permission"""

    # --- Verify if 1,1,1 exists and is_deleted=0 ---
    existing_up = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )

    if existing_up:
        up_id = existing_up.id
    else:
        # Add new user permission if not exists
        up = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(up)
        db_session.commit()
        up_id = up.id

    # --- Act: perform soft delete ---
    result = UserPerm_DBConn.deleteUP(up_id, db_session)

    # --- Assert: check response and DB state ---
    assert result is True
    updated_up = db_session.query(UserPermission).filter_by(id=up_id).first()
    assert updated_up.is_deleted == 1

    # --- Revert: reset is_deleted back to 0 if it existed before, else delete it ---
    if existing_up:
        updated_up.is_deleted = 0
        db_session.commit()
    else:
        db_session.query(UserPermission).filter_by(id=up_id).delete()
        db_session.commit()


def test_delete_up_exception(db_session):
    """Test soft deletion of a user permission with exception"""

    # --- Verify if 1,1,1 exists and is_deleted=0 ---
    existing_up = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )

    if existing_up:
        up_id = existing_up.id
    else:
        # Add a new record if not exists
        up = UserPermission(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        db_session.add(up)
        db_session.commit()
        up_id = up.id

    # --- Mock commit to throw exception ---
    with patch("sqlalchemy.orm.Session.commit", side_effect=Exception("Test error")):
        # Act
        result = UserPerm_DBConn.deleteUP(up_id, db_session)

        # Assert
        assert result is False

    # --- Cleanup / Revert ---
    if existing_up:
        # Ensure the original record is not marked deleted due to rollback
        up_obj = db_session.query(UserPermission).filter_by(id=up_id).first()
        up_obj.is_deleted = 0
        db_session.commit()
    else:
        # If test record, delete it
        db_session.query(UserPermission).filter_by(id=up_id).delete()
        db_session.commit()


# * DELETE UP ENDED
