from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from dao.v1.role_dao import Role_DBConn
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/role/getrole")

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
    mock_serv.return_value = {
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
    }
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/role/getrole?role_id=1")

    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["message"] == "Fetched single role successfully."


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_invalid_role_id(mock_serv, client, get_valid_token):
    """Test fetching role with non-digit role_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/role/getrole?role_id=abc")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_non_existent_role(mock_serv, client, get_valid_token):
    """Test fetching role with non-existent role_id"""
    mock_serv.return_value = JSONResponse(
        content={"message": "Role not found.", "success": False}, status_code=400
    )
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/role/getrole?role_id=999")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Role not found."
    assert json_data["success"] is False


@patch("services.v1.role_services.Role_Services.getRole_serv")
def test_get_role_unexpected_error(mock_serv, client, get_valid_token):
    """Test fetching role with unexpected error"""
    mock_serv.side_effect = Exception("Database error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/role/getrole?role_id=1")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Database error"


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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rolename": "NewRole", "status": 1}
    response = client.post("/v1/role/addrole", json=payload)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == True


def test_add_role_missing_rolename(client, get_valid_token):
    """Test role creation with missing rolename"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rolename": "", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Role name is missing."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_add_role_duplicate_rolename(mock_get_role_data, client, get_valid_token):
    """Test role creation with duplicate rolename"""
    mock_role = MagicMock(rolename="Admin")
    mock_get_role_data.return_value = [mock_role]
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rolename": "Admin", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
@patch("dao.v1.role_dao.Role_DBConn.createRole")
def test_add_role_creation_failed(
    mock_create_role, mock_get_role_data, client, get_valid_token
):
    """Test role creation when DAO fails"""
    mock_get_role_data.return_value = []  # No existing roles
    mock_create_role.return_value = False
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rolename": "NewRole", "status": "admin"}
    response = client.post("/v1/role/addrole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_add_role_unexpected_error(mock_get_role_data, client, get_valid_token):
    """Test role creation with unexpected error"""
    mock_get_role_data.side_effect = Exception("Database error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rolename": "NewRole", "status": "1"}
    response = client.post("/v1/role/addrole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST


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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "1", "rolename": "NewRole", "status": "2"}
    response = client.patch("/v1/role/updaterole", json=payload)

    print("response Data ", response.text)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == True
    assert json_data["message"] == "Role updated successfully."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_invalid_role_id(mock_get_role_data, client, get_valid_token):
    """Test role update with invalid role_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "abc", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_non_existent_role(mock_get_role_data, client, get_valid_token):
    """Test role update with non-existent role_id"""
    mock_get_role_data.return_value = []
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "999", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload)
    print(response.text)
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "1", "rolename": "", "status": ""}
    response = client.patch("/v1/role/updaterole", json=payload)

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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 1, "rolename": "NewRole", "status": 2}
    response = client.patch("/v1/role/updaterole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "Role update failed."


@patch("dao.v1.role_dao.Role_DBConn.getRoleData")
def test_update_role_unexpected_error(mock_get_role_data, client, get_valid_token):
    """Test role update with unexpected error"""
    mock_get_role_data.side_effect = Exception("Database error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "1", "rolename": "NewRole", "status": "1"}
    response = client.patch("/v1/role/updaterole", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "Database error"


# INTEGRATION TEST ENDED
# * UPDATE ROLE ENDED


# * DELETE ROLE STARTED


# UNIT TEST STARTED
def test_delete_role_invalid_role_id(client, get_valid_token):
    """Test role deletion with non-digit role_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/role/deleterole?role_id=abc")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_delete_role_missing_role_id(client, get_valid_token):
    """Test role deletion with missing role_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/role/deleterole")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_role_success(client, get_valid_token, db_session):
    db_session.query(Role).filter(Role.id == 4).update({"is_deleted": 0})
    db_session.commit()
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/role/deleterole?role_id=4")
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == True
    assert json_data["message"] == "Role deleted successfully."


# UNIT TEST ENDED
# * DELETE ROLE ENDED
