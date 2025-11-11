from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from model.v1.user_model import Role
from tests.v1.conftest import db_session


# * GET ROLE STARTED
# UNIT TEST STARTED


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_all(mock_serv, client, get_valid_token):
    """Test fetching all roles when role_id is not provided"""
    mock_serv.return_value = JSONResponse(
        content={
            "message": "Fetched all roles successfully.",
            "roles": [
                {
                    "id": 1,
                    "rolename": "Admin",
                    "status": 1,
                    "created_by": 1,
                    "modified_by": 1,
                    "created_at": "2025-07-29T10:00:00",
                    "modified_at": "2025-07-29T10:00:00",
                },
                {
                    "id": 2,
                    "rolename": "User",
                    "status": 1,
                    "created_by": 1,
                    "modified_by": 1,
                    "created_at": "2025-07-29T10:00:00",
                    "modified_at": "2025-07-29T10:00:00",
                },
            ],
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/role/getrole", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["message"] == "Fetched all roles successfully."
    assert len(json_data["roles"]) == 2
    assert json_data["roles"][0]["id"] == 1
    assert json_data["roles"][0]["rolename"] == "Admin"
    assert json_data["roles"][1]["id"] == 2
    assert json_data["roles"][1]["rolename"] == "User"


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_single_role(mock_serv, client, get_valid_token):
    """Test fetching a single role with valid role_id"""
    mock_serv.return_value = JSONResponse(
        content={
            "message": "Fetched single role successfully.",
            "roles": [
                {
                    "id": 1,
                    "rolename": "Admin",
                    "status": 1,
                    "created_by": 1,
                    "modified_by": 1,
                    "created_at": "2025-07-29T10:00:00",
                    "modified_at": "2025-07-29T10:00:00",
                }
            ],
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/role/getrole?role_id=1", headers=headers)

    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["message"] == "Fetched single role successfully."


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_invalid_role_id(mock_serv, client, get_valid_token):
    """Test fetching role with non-digit role_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/role/getrole?role_id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_non_existent_role(mock_serv, client, get_valid_token):
    """Test fetching role with non-existent role_id"""
    mock_serv.return_value = JSONResponse(
        content={"message": "Role not found.", "success": False}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/role/getrole?role_id=999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Role not found."
    assert json_data["success"] is False


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_unexpected_error(mock_serv, client, get_valid_token):
    """Test fetching role with unexpected error"""
    mock_serv.side_effect = Exception("Database error")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/role/getrole?role_id=1", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Database error"


def test_get_role_missing_token(client):
    """Test fetching role without token"""
    headers = {"Accept-Language": "en"}
    response = client.get("/v1/role/getrole", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# UNIT TEST ENDED
# * GET ROLE ENDED

# * ADD ROLE STARTED


# UNIT TEST STARTED
@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.createRole")
def test_add_role_success(
    mock_create_role, mock_get_role_data, client, get_valid_token
):
    """Test successful role creation"""
    mock_get_role_data.return_value = []  # No existing roles
    mock_create_role.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"rolename": "NewRole", "status": 1}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == "true"


def test_add_role_missing_rolename(client, get_valid_token):
    """Test role creation with missing rolename"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"rolename": "", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Role Name is missing."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_add_role_duplicate_rolename(mock_get_role_data, client, get_valid_token):
    """Test role creation with duplicate rolename"""
    mock_role = MagicMock(rolename="Admin")
    mock_get_role_data.return_value = [mock_role]
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"rolename": "Admin", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "Role Name Already exists."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.createRole")
def test_add_role_creation_failed(
    mock_create_role, mock_get_role_data, client, get_valid_token
):
    """Test role creation when DAO fails"""
    mock_get_role_data.return_value = []  # No existing roles
    mock_create_role.return_value = False
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"rolename": "NewRole", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "Role Creation failed"


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_add_role_unexpected_error(mock_get_role_data, client, get_valid_token):
    """Test role creation with unexpected error"""
    mock_get_role_data.side_effect = Exception("Database error")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"rolename": "NewRole", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


def test_add_role_missing_token(client):
    """Test role creation without token"""
    headers = {"Accept-Language": "en"}
    payload = {"rolename": "NewRole", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED
# * ADD ROLE ENDED


# * UPDATE ROLE STARTED
# UNIT TEST STARTED
@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.updateRoleDB")
def test_update_role_success(
    mock_update_role_db, mock_get_role_data, client, get_valid_token
):
    """Test successful role update"""
    mock_role = MagicMock(id=1, rolename="OldRole", status=1, modified_by="1")
    mock_get_role_data.return_value = [mock_role]
    mock_update_role_db.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": "1", "rolename": "NewRole", "status": "2"}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    print("response Data ", response.text)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == "true"
    assert json_data["message"] == "Role Updated Successfully"


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_invalid_role_id(mock_get_role_data, client, get_valid_token):
    """Test role update with invalid role_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": "abc", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_non_existent_role(mock_get_role_data, client, get_valid_token):
    """Test role update with non-existent role_id"""
    mock_get_role_data.return_value = []
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": "999", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)
    print(response.text)
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "Role not found."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.updateRoleDB")
def test_update_role_empty_fields(
    mock_update_role_db, mock_get_role_data, client, get_valid_token
):
    """Test role update with empty rolename and status"""
    mock_role = MagicMock(id=1, rolename="OldRole", status="1", modified_by="1")
    mock_get_role_data.return_value = [mock_role]
    mock_update_role_db.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": "1", "rolename": "", "status": ""}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.updateRoleDB")
def test_update_role_update_failed(
    mock_update_role_db, mock_get_role_data, client, get_valid_token
):
    """Test role update when DAO fails"""
    mock_role = MagicMock(id=1, rolename="OldRole", status=1, modified_by=1)
    mock_get_role_data.return_value = [mock_role]
    mock_update_role_db.return_value = False
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": 1, "rolename": "NewRole", "status": 2}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "Role Update failed"


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_unexpected_error(mock_get_role_data, client, get_valid_token):
    """Test role update with unexpected error"""
    mock_get_role_data.side_effect = Exception("Database error")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"role_id": "1", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "Database error"


def test_update_role_missing_token(client):
    """Test role update without token"""
    headers = {"Accept-Language": "en"}
    payload = {"role_id": "1", "rolename": "NewRole", "status": 1}
    response = client.patch("/v1/role/updaterole", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN


# INTEGRATION TEST ENDED
# * UPDATE ROLE ENDED


# * DELETE ROLE STARTED


# UNIT TEST STARTED
def test_delete_role_invalid_role_id(client, get_valid_token):
    """Test role deletion with non-digit role_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.delete("/v1/role/deleterole?role_id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# @patch("controllers.v1.role_controller.verifyRoleID")
# def test_delete_role_non_existent_role(mock_verify_role_id, client, get_valid_token):
#     """Test role deletion with non-existent role_id"""
#     mock_verify_role_id.return_value = JSONResponse(
#         content={"success": False, "message": "Role not found."}, status_code=400
#     )
#     headers = {"Authorization": f"Bearer {get_valid_token}"}
#     response = client.delete("/v1/role/deleterole?role_id=99999", headers=headers)
#     print(response.text)

#     assert response.status_code == HTTP_400_BAD_REQUEST
#     json_data = response.json()
#     assert json_data["success"] == False
#     assert json_data["message"] == "Role not found."


def test_delete_role_missing_token(client):
    """Test role deletion without token"""
    headers = {"Accept-Language": "en"}
    response = client.delete("/v1/role/deleterole?role_id=1", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


def test_delete_role_missing_role_id(client, get_valid_token):
    """Test role deletion with missing role_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.delete("/v1/role/deleterole", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_role_success(client, get_valid_token, db_session):
    db_session.query(Role).filter(Role.id == 4).update({"is_deleted": 0})
    db_session.commit()
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.delete("/v1/role/deleterole?role_id=4", headers=headers)
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == "true"
    assert json_data["message"] == "Role Deleted Successfully."


# UNIT TEST ENDED
# * DELETE ROLE ENDED
