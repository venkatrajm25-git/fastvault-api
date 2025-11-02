from unittest.mock import patch
from dao.v1.perm_dao import Permissions_DBConn
from fastapi.responses import JSONResponse

# from helpers.v1.helpers import deletePermission
import json
from model.v1.permission_model import Permission
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from tests.v1.conftest import get_or_create_by_name


# * GET ALL PERMISSION STARTED
# UNIT TEST STARTED
def test_get_permission_invalid_id_format(client, get_valid_token):
    """Test fetching a permission with non-digit permission_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/perm/getpermission?permission_id=id", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_get_all_permissions(client, get_valid_token, db_session):
    """Test fetching all permissions"""
    # Setup test data
    permissionData = db_session.query(Permission).all()
    if not permissionData:
        NewPermission = Permission(name="Create")
        db_session.add(NewPermission)
        db_session.commit()
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/perm/getpermission", headers=headers)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "data fetched successfully" in json_data["message"].lower()
    assert "data" in json_data


# Additional test cases
def test_get_single_permission(client, get_valid_token, db_session):
    """Test fetching a single permission by permission_id"""
    # Setup test data
    permissionData = db_session.query(Permission).all()
    if not permissionData:
        NewPermission = Permission(name="Create")
        db_session.add(NewPermission)
        db_session.commit()

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/perm/getpermission?permission_id=1", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "data fetched successfully" in json_data["message"].lower()
    assert "data" in json_data


def test_get_permission_non_existent_id(client, get_valid_token, db_session):
    """Test fetching a permission with non-existent permission_id"""
    # Ensure no permission with id=999 exists
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/perm/getpermission?permission_id=99999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "not found" in json_data["message"].lower()


def test_get_permission_database_error(client, get_valid_token):
    """Test fetching a permission with database error"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.getPermission_Serv",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.get("/v1/perm/getpermission?permission_id=1", headers=headers)
        print("response", response.text)
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "database connection failed" in json_data["message"].lower()


def test_get_permission_different_language(client, get_valid_token, db_session):
    """Test fetching a permission with different Accept-Language header"""
    # Setup test data
    permissionData = db_session.query(Permission).all()
    if not permissionData:
        NewPermission = Permission(name="Create")
        db_session.add(NewPermission)
        db_session.commit()
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.get("/v1/perm/getpermission?permission_id=1", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"
    assert "data" in json_data


def test_get_permission_invalid_token(client):
    """Test fetching a permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.get("/v1/perm/getpermission?permission_id=1", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# UNIT TEST ENDED

# * GET ALL PERMISSION ENDED


# * ADD PERMISSION STARTED
# UNIT TEST STARTED


def test_add_permission_missing_name(client, get_valid_token):
    """Test adding a permission without a name"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post(
        "/v1/perm/addpermission",
        json={"current user": {"user_id": 1}},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "mandatory" in json_data["message"].lower()


def test_add_permission_already_exists(client, get_valid_token, db_session):
    """Test adding a permission that already exists"""
    # Setup test data
    dummyPermission = get_or_create_by_name(
        db_session, Permission, name_value="TestPermission"
    )
    id = dummyPermission.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": "TestPermission",
            "current user": {"user_id": 1},
        },
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"

    # Clean up
    db_session.query(Permission).filter(Permission.name == "TestPermission").delete()
    db_session.commit()


# Replacement for test_add_permission_success
def test_add_permission_success(client, get_valid_token, db_session):
    """Test successful addition of a permission via API"""
    # Setup test data
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": "TestPermission",
            "current user": {"user_id": 1},
        },
        headers=headers,
    )
    print(response.text)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "permission added" in json_data["message"].lower()

    # Clean up
    db_session.query(Permission).filter(Permission.name == "TestPermission").delete()
    db_session.commit()


def test_add_permission_database_error(client, get_valid_token, db_session):
    """Test adding a permission with general database error"""
    # dummyPermission = Permission(name="ErrorPermission")
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
            headers=headers,
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False
        assert "database connection failed" in json_data["error"].lower()

    # Clean up
    db_session.query(Permission).filter(Permission.name == "ErrorPermission").delete()
    db_session.commit()


def test_add_permission_different_language(client, get_valid_token, db_session):
    """Test adding a permission with different Accept-Language header"""
    permission_name = "LangPermission"
    db_session.query(Permission).filter(Permission.name == permission_name).delete()
    db_session.commit()

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": permission_name,
            "current user": {"user_id": 1},
        },
        headers=headers,
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "permission added" in json_data["message"].lower()

    # Clean up
    db_session.query(Permission).filter(Permission.name == permission_name).delete()
    db_session.commit()


def test_add_permission_invalid_token(client):
    """Test adding a permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.post(
        "/v1/perm/addpermission",
        json={
            "name": "TestPermission",
            "current user": {"user_id": 1},
        },
        headers=headers,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED

# * ADD PERMISSION ENDED

# * UPDATE PERMISSION ENDED


# UNIT TEST STARTED
def test_update_permission_missing_permission_id(client, get_valid_token):
    """Test updating a permission without permission_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission", json={"name": "UpdatedPermission"}, headers=headers
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
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": "99999", "name": "NewPermission"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "not available" in json_data["message"].lower()


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

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": OtherPermissionID, "name": "ExistingPermission"},
        headers=headers,
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
        db_session, Permission, name_value="ExistingPermission"
    )
    ExistingPermissionID = ExistingPermission.id

    OtherPermission = get_or_create_by_name(
        db_session, Permission, name_value="OtherPermission"
    )
    OtherPermissionID = OtherPermission.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": OtherPermissionID, "name": "UpdatedPermission"},
        headers=headers,
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
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
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": "invalid", "name": "NewPermission"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data


def test_update_permission_database_error(client, get_valid_token, db_session):
    """Test updating a permission with general database error"""
    permissionData = (
        db_session.query(Permission)
        .filter(Permission.name == "TestingPermission")
        .first()
    )
    if not permissionData:
        NewPermission = Permission(name="TestingPermission")
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
        headers = {
            "Authorization": f"Bearer {get_valid_token}",
            "Accept-Language": "en",
        }
        response = client.patch(
            "/v1/perm/updatepermission",
            json={"permission_id": permissionData.id, "name": "UpdatedPermission"},
            headers=headers,
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


def test_update_permission_different_language(client, get_valid_token, db_session):
    """Test updating a permission with different Accept-Language header"""
    # Setup test data
    ExistingPermission = get_or_create_by_name(
        db_session, Permission, name_value="ExistingPermission"
    )
    ExistingPermissionID = ExistingPermission.id

    OtherPermission = get_or_create_by_name(
        db_session, Permission, name_value="OtherPermission"
    )
    OtherPermissionID = OtherPermission.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": OtherPermissionID, "name": "UpdatedPermission"},
        headers=headers,
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data

    # Clean up
    db_session.query(Permission).filter(
        Permission.id.in_([OtherPermissionID, ExistingPermissionID])
    ).delete()
    db_session.commit()


def test_update_permission_invalid_token(client):
    """Test updating a permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.patch(
        "/v1/perm/updatepermission",
        json={"permission_id": "1", "name": "NewPermission"},
        headers=headers,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED
# * UPDATE PERMISSION ENDED


# * DELETE PERMISSION STARTED
# UNIT TEST STARTED


def test_delete_permission_missing_id(client, get_valid_token):
    """Test deleting a permission without permission_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete(
        "/v1/perm/deletepermission?permission_id=", headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_permission_invalid_id_format(client, get_valid_token):
    """Test deleting a permission with non-digit permission_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete(
        "/v1/perm/deletepermission?permission_id=abc", headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_permission_non_existent_id(client, get_valid_token, db_session):
    """Test deleting a permission with non-existent permission_id"""

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete(
        "/v1/perm/deletepermission?permission_id=99999", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "not found" in json_data["message"].lower()


# Replacement for test_delete_permission_success
def test_delete_permission_success(client, get_valid_token, db_session):
    """Test successful deletion of a permission via API"""
    # Setup test data
    dummyPermission = Permission(name="TestPermission")
    db_session.add(dummyPermission)
    db_session.commit()
    db_session.refresh(dummyPermission)

    id = dummyPermission.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete(
        f"/v1/perm/deletepermission?permission_id={id}", headers=headers
    )
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
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
        response = client.delete(
            f"/v1/perm/deletepermission?permission_id={id}", headers=headers
        )
        print(response.text)
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "database connection failed" in json_data["message"].lower()
        db_session.query(Permission).filter(Permission.id == id).delete()
        db_session.commit()


def test_delete_permission_different_language(client, get_valid_token, db_session):
    """Test deleting a permission with different Accept-Language header"""
    # Setup test data
    dummyPermission = get_or_create_by_name(
        db_session, Permission, name_value="TestPermission"
    )
    id = dummyPermission.id
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.delete(
        f"/v1/perm/deletepermission?permission_id={id}", headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"

    # Clean up
    db_session.query(Permission).filter(Permission.id == id).delete()
    db_session.commit()


def test_delete_permission_invalid_token(client):
    """Test deleting a permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.delete(
        "/v1/perm/deletepermission?permission_id=10", headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED

# * DELETE PERMISSION ENDED
