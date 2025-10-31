from unittest.mock import patch, MagicMock
from services.v1.user_services import user_databaseConnection
from fastapi.responses import JSONResponse
from database.v1.connection import getDBConnection
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from datetime import datetime

# * GET ALL USER STARTED
# UNIT TEST STARTED


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_all_users_success(mock_get_user_table, client, get_valid_token):
    """Test fetching all users successfully"""
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        username="testuser",
        status=1,
        role=1,
        created_by=1,
        modified_by=1,
        created_at=datetime(2024, 1, 1),
        modified_at=datetime(2024, 1, 2),
    )
    mock_get_user_table.return_value = [mock_user]
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == "true"


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_single_user_success(mock_get_user_table, client, get_valid_token):
    """Test fetching a single user successfully"""
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        username="testuser",
        status=1,
        role=1,
        created_by=1,
        modified_by=1,
        created_at=datetime(2024, 1, 1),
        modified_at=datetime(2024, 1, 2),
    )
    mock_get_user_table.return_value = [mock_user]
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser?id=1", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == "true"


def test_get_user_invalid_id(client, get_valid_token):
    """Test fetching user with non-integer id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser?id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data
    assert any("id" in error["loc"] for error in json_data["detail"])


@patch("controllers.v1.user_controller.user_services.getAlluser_serv")
def test_get_user_non_existent_id(mock_verify_id, client, get_valid_token):
    """Test fetching user with non-existent id"""
    mock_verify_id.return_value = JSONResponse(
        content={"success": False, "message": "User not found."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser?id=999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "User not found."


def test_get_user_not_found(client, get_valid_token):
    """Test fetching user with non-existent id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser?id=99999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_user_database_error(mock_get_user_table, client, get_valid_token):
    """Test fetching users with database error"""
    mock_get_user_table.return_value = {
        "success": False,
        "error": "Database Connection Error.",
    }
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["error"] == "Database Connection Error."


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_user_unexpected_error(mock_get_user_table, client, get_valid_token):
    """Test fetching users with unexpected error"""
    mock_get_user_table.side_effect = Exception("Unexpected error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/user/getuser", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Unexpected error"


def test_get_user_missing_token(client):
    """Test fetching users without token"""
    headers = {"Accept-Language": "en"}
    response = client.get("/v1/user/getuser", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# UNIT TEST ENDED
# * GET ALL USER ENDED


# * UPDATE USER STARTED
# UNIT TEST STARTED
@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_success(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test successful user update"""
    mock_user = MagicMock(id=1, username="olduser", status=1, role=1, modified_by="1")
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == "true"
    assert json_data["message"] == "User Updated Successfully"


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_partial_fields(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test user update with partial fields"""
    mock_user = MagicMock(id=1, username="olduser", status=1, role=3, modified_by=1)
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 1, "username": "newuser"}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == "true"
    assert json_data["message"] == "User Updated Successfully"


def test_update_user_missing_id(client, get_valid_token):
    """Test user update with missing id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_update_user_non_existent_id(mock_get_user_table, client, get_valid_token):
    """Test user update with non-existent id"""
    mock_get_user_table.return_value = []
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 999, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "User not found."


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_empty_fields(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test user update with empty fields"""
    mock_user = MagicMock(id=1, username="olduser", status=2, role=3, modified_by=1)
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == "true"
    assert json_data["message"] == "User Updated Successfully"


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_update_failed(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test user update when DAO fails"""
    mock_user = MagicMock(id=1, username="olduser", status=1, role=1, modified_by=1)
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = False
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "User Update failed"


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_update_user_unexpected_error(mock_get_user_table, client, get_valid_token):
    """Test user update with unexpected error"""
    mock_get_user_table.side_effect = Exception("Database error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


def test_update_user_missing_token(client):
    """Test user update without token"""
    headers = {"Accept-Language": "en"}
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED

# * UPDATE USER ENDED


# * DELETE USER STARTED
# UNIT TEST STARTED
@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_success(mock_delete_user_db, client, get_valid_token):
    """Test successful user deletion"""
    mock_delete_user_db.return_value = True
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser?id=1", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    print(json_data)
    assert json_data["success"] == "true"
    assert json_data["message"] == "User Deleted Successfully."


def test_delete_user_missing_id(client, get_valid_token):
    """Test user deletion with missing id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_delete_user_invalid_id(client, get_valid_token):
    """Test user deletion with non-integer id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser?id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_non_existent_id(mock_delete_user_db, client, get_valid_token):
    """Test user deletion with non-existent id"""
    mock_delete_user_db.return_value = False
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser?id=99999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == "false"
    assert json_data["message"] == "User deletion failed"


@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_unexpected_error(mock_delete_user_db, client, get_valid_token):
    """Test user deletion with unexpected error"""
    mock_delete_user_db.side_effect = Exception("Database error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser?id=1", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "Database error"


def test_delete_user_missing_token(client):
    """Test user deletion without token"""
    headers = {"Accept-Language": "en"}
    response = client.delete("/v1/user/deleteuser?id=1", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# INTEGRATION TEST ENDED
# * DELETE USER ENDED
