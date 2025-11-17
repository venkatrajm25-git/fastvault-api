from os import name
from unittest.mock import patch
from urllib import response
from dao.v1.perm_dao import Permissions_DBConn
from fastapi.responses import JSONResponse

# from helpers.v1.helpers import deletePermission
import json
from model.v1.permission_model import Permission
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
)

from tests.v1.conftest import get_or_create_by_name


# * GET ALL PERMISSION STARTED
# UNIT TEST STARTED
# @patch("middleware.v1.auth_token.is_token_blacklisted", return_value=False)
def test_get_permission_invalid_id_format(client, get_valid_token):
    """
    Test that passing a non-digit permission_id ('id')
    results in 422 Unprocessable Entity.
    """

    # Clear old cookies
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # Call API with invalid permission_id
    response = client.get("/v1/perm/getpermission?permission_id=id")

    print("Response:", response.text)

    # FastAPI should block this before controller logic runs
    assert response.status_code == 422

    json_body = response.json()
    assert "detail" in json_body


def test_get_all_permissions(client, get_valid_token, db_session):
    """Test fetching all permissions"""
    # Setup test data
    permissionData = db_session.query(Permission).all()
    if not permissionData:
        NewPermission = Permission(permission_name="Create")
        db_session.add(NewPermission)
        db_session.commit()
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/perm/getpermission")
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "data fetched successfully" in json_data["message"].lower()
    assert "data" in json_data


# Additional test cases
def test_get_single_permission(client, get_valid_token, db_session):
    """Test fetching a single permission by permission_id"""
    # Setup test data
    permissionData = db_session.query(Permission).all()
    if not permissionData:
        NewPermission = Permission(permission_name="Create")
        db_session.add(NewPermission)
        db_session.commit()

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/perm/getpermission?permission_id=1")

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "data fetched successfully" in json_data["message"].lower()
    assert "data" in json_data


def test_get_permission_non_existent_id(client, get_valid_token, db_session):
    """Test fetching a permission with non-existent permission_id"""
    # Ensure no permission with id=999 exists
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/perm/getpermission?permission_id=99999")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "not found" in json_data["message"].lower()


def test_get_permission_database_error(client, get_valid_token):
    """Test fetching a permission with database error"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.getPermission_Serv",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.get("/v1/perm/getpermission?permission_id=1")
        print("response", response.text)
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "database connection failed" in json_data["message"].lower()


# UNIT TEST ENDED

# * GET ALL PERMISSION ENDED


# * ADD PERMISSION STARTED
# UNIT TEST STARTED


def test_add_permission_missing_name(client, get_valid_token):
    """Test adding a permission without a name"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/addpermission",
        json={"current user": {"user_id": 1}},
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "mandatory" in json_data["message"].lower()


def test_add_permission_already_exists(client, get_valid_token, db_session):
    """Test adding a permission that already exists"""
    # Setup test data
    dummyPermission = get_or_create_by_name(
        db_session, Permission, name_value="TestPermission"
    )
    id = dummyPermission.id

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": "TestPermission",
            "current user": {"user_id": 1},
        },
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False

    # Clean up
    db_session.query(Permission).filter(
        Permission.permission_name == "TestPermission"
    ).delete()
    db_session.commit()


# Replacement for test_add_permission_success
def test_add_permission_success(client, get_valid_token, db_session):
    """Test successful addition of a permission via API"""
    # Setup test data
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": "TestPermission",
            "current user": {"user_id": 1},
        },
    )
    print(response.text)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "permission added" in json_data["message"].lower()

    # Clean up
    db_session.query(Permission).filter(
        Permission.permission_name == "TestPermission"
    ).delete()
    db_session.commit()


def test_add_permission_database_error(client, get_valid_token, db_session):
    """Test adding a permission with general database error"""
    # dummyPermission = Permission(permission_name="ErrorPermission")
    # db_session.add(dummyPermission)
    # db_session.commit()
    # db_session.refresh(dummyPermission)

    # id = dummyPermission.id

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.addPermission_Serv",
        return_value=JSONResponse(
            content={"success": False, "error": "database connection failed"},
            status_code=400,
        ),
    ):
        headers = {
            "Authorization": f"Bearer {get_valid_token}",
            "Accept-Language": "en",
        }
        response = client.post(
            "/v1/perm/addpermission",
            json={
                "name": "ErrorPermission",
                "current user": {"user_id": 1},
            },
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False

    # Clean up
    db_session.query(Permission).filter(
        Permission.permission_name == "ErrorPermission"
    ).delete()
    db_session.commit()


# INTEGRATION TEST ENDED

# * ADD PERMISSION ENDED

# * UPDATE PERMISSION ENDED


# UNIT TEST STARTED
def test_update_permission_missing_permission_id(client, get_valid_token):
    """Test updating a permission without permission_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updatepermission", json={"name": "UpdatedPermission"}
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "mandatory" in json_data["message"].lower()


def test_update_permission_non_existent_id(client, get_valid_token, db_session):
    """Test updating a permission with non-existent permission_id"""
    # Ensure no permission with id=999 exists
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": "99999", "name": "NewPermission"},
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False


@patch("controllers.v1.perm_controller.Perm_Serv.updatePerm_Serv")
def test_update_permission_duplicate_name(
    mock_update, client, get_valid_token, db_session
):
    """Test updating a permission to a duplicate name"""
    # Setup test data
    ExistingPermission = get_or_create_by_name(
        db_session, Permission, name_value="ExistingPermission"
    )
    ExistingPermissionID = ExistingPermission.id

    OtherPermission = get_or_create_by_name(
        db_session, Permission, name_value="OtherPermission"
    )
    OtherPermissionID = OtherPermission.id

    mock_update.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": OtherPermissionID, "name": "ExistingPermission"},
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "duplicate entry" in json_data["error"].lower()

    # Clean up
    db_session.query(Permission).filter(
        Permission.id.in_([OtherPermissionID, ExistingPermissionID])
    ).delete()
    db_session.commit()


# Replacement for test_update_permission_success
def test_update_permission_success(client, get_valid_token, db_session):
    """Test successful update of a permission via API"""
    # Setup test data
    ExistingPermission = get_or_create_by_name(
        db_session,
        Permission,
        name_field="permission_name",
        name_value="ExistingPermission",
    )
    ExistingPermissionID = ExistingPermission.id

    OtherPermission = get_or_create_by_name(
        db_session,
        Permission,
        name_field="permission_name",
        name_value="OtherPermission",
    )
    OtherPermissionID = OtherPermission.id

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": OtherPermissionID, "name": "UpdatedPermission"},
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "updated successfully" in json_data["message"].lower()

    # Verify database
    # permission = db_session.query(Permission).filter(Permission.id == 1).first()
    # assert permission is not None
    # assert permission.name == "UpdatedPermission"

    # Clean up
    db_session.query(Permission).filter(
        Permission.id.in_([OtherPermissionID, ExistingPermissionID])
    ).delete()
    db_session.commit()


# Additional test cases
def test_update_permission_invalid_id_format(client, get_valid_token):
    """Test updating a permission with non-integer permission_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": "invalid", "name": "NewPermission"},
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data


def test_update_permission_database_error(client, get_valid_token, db_session):
    """Test updating a permission with general database error"""
    permissionData = (
        db_session.query(Permission)
        .filter(Permission.permission_name == "TestingPermission")
        .first()
    )
    if not permissionData:
        NewPermission = Permission(permission_name="TestingPermission")
        db_session.add(NewPermission)
        db_session.commit()
        db_session.refresh(NewPermission)
        permissionData = NewPermission

    db_session.commit()
    with patch(
        "controllers.v1.perm_controller.Perm_Serv.updatePerm_Serv",
        return_value=JSONResponse(
            content={"success": False, "error": "Database connection failed"},
            status_code=400,
        ),
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        response = client.patch(
            "/v1/perm/updatepermission",
            json={"permission_id": permissionData.id, "name": "UpdatedPermission"},
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False
        assert "database connection failed" in json_data["error"].lower()

    # Clean up
    db_session.query(Permission).filter(Permission.id == permissionData.id).delete()
    db_session.commit()


# INTEGRATION TEST ENDED
# * UPDATE PERMISSION ENDED


# * DELETE PERMISSION STARTED
# UNIT TEST STARTED


def test_delete_permission_missing_id(client, get_valid_token):
    """Test deleting a permission without permission_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deletepermission?permission_id=")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_permission_invalid_id_format(client, get_valid_token):
    """Test deleting a permission with non-digit permission_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deletepermission?permission_id=abc")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_permission_non_existent_id(client, get_valid_token, db_session):
    """Test deleting a permission with non-existent permission_id"""

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deletepermission?permission_id=99999")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "not found" in json_data["message"].lower()


# Replacement for test_delete_permission_success
def test_delete_permission_success(client, get_valid_token, db_session):
    """Test successful deletion of a permission via API"""
    # Setup test data
    dummyPermission = Permission(permission_name="TestPermission")
    db_session.add(dummyPermission)
    db_session.commit()
    db_session.refresh(dummyPermission)

    id = dummyPermission.id

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete(f"/v1/perm/deletepermission?permission_id={id}")
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "deleted successfully" in json_data["message"].lower()
    db_session.query(Permission).filter(Permission.id == id).delete()
    db_session.commit()


def test_delete_permission_database_error(client, get_valid_token, db_session):
    """Test deleting a permission with general database error"""
    # Setup test data
    dummyPermission = get_or_create_by_name(
        db_session, Permission, name_value="TestPermission"
    )
    id = dummyPermission.id
    with patch(
        "controllers.v1.perm_controller.Perm_Serv.deletePermission_Serv",
        side_effect=Exception("Database connection failed"),
    ):
        headers = {
            "Authorization": f"Bearer {get_valid_token}",
            "Accept-Language": "en",
        }
        response = client.delete(f"/v1/perm/deletepermission?permission_id={id}")
        print(response.text)
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "database connection failed" in json_data["message"].lower()
        db_session.query(Permission).filter(Permission.id == id).delete()
        db_session.commit()


# INTEGRATION TEST ENDED

# * DELETE PERMISSION ENDED
