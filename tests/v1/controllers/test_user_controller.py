from unittest.mock import patch, MagicMock
from services.v1.user_services import user_databaseConnection
from fastapi.responses import JSONResponse
from database.v1.connection import getDBConnection
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_CONTENT,
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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser")
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == True


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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser?id=1")

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] == True


def test_get_user_invalid_id(client, get_valid_token):
    """Test fetching user with non-integer id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser?id=abc")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data
    assert any("id" in error["loc"] for error in json_data["detail"])


@patch("controllers.v1.user_controller.user_services.getAlluser_serv")
def test_get_user_non_existent_id(mock_verify_id, client, get_valid_token):
    """Test fetching user with non-existent id"""
    mock_verify_id.return_value = JSONResponse(
        content={"success": False, "message": "User not found."}, status_code=400
    )
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser?id=999")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "User not found."


def test_get_user_not_found(client, get_valid_token):
    """Test fetching user with non-existent id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser?id=99999")

    assert response.status_code == HTTP_400_BAD_REQUEST


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_user_database_error(mock_get_user_table, client, get_valid_token):
    """Test fetching users with database error"""
    mock_get_user_table.return_value = {
        "success": False,
        "error": "Database Connection Error.",
    }
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser")

    assert response.status_code == HTTP_400_BAD_REQUEST


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_get_user_unexpected_error(mock_get_user_table, client, get_valid_token):
    """Test fetching users with unexpected error"""
    mock_get_user_table.side_effect = Exception("Unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.get("/v1/user/getuser")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Unexpected error"


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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] == True
    assert json_data["message"] == "User updated successfully."


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_partial_fields(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test user update with partial fields"""
    mock_user = MagicMock(id=1, username="olduser", status=1, role=3, modified_by=1)
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = True
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 1, "username": "newuser"}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_update_user_missing_id(client, get_valid_token):
    """Test user update with missing id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_update_user_non_existent_id(mock_get_user_table, client, get_valid_token):
    """Test user update with non-existent id"""
    mock_get_user_table.return_value = []
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 999, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

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
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
@patch("dao.v1.user_dao.user_databaseConnection.updateUser")
def test_update_user_update_failed(
    mock_update_user, mock_get_user_table, client, get_valid_token
):
    """Test user update when DAO fails"""
    mock_user = MagicMock(id=1, username="olduser", status=1, role=1, modified_by=1)
    mock_get_user_table.return_value = [mock_user]
    mock_update_user.return_value = False
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "User update failed."


@patch("dao.v1.user_dao.user_databaseConnection.getUserTable")
def test_update_user_unexpected_error(mock_get_user_table, client, get_valid_token):
    """Test user update with unexpected error"""
    mock_get_user_table.side_effect = Exception("Database error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"id": 1, "username": "newuser", "status": 1, "role": 1}
    response = client.patch("/v1/user/updateuser", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED

# * UPDATE USER ENDED


# * DELETE USER STARTED
# UNIT TEST STARTED
@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_success(mock_delete_user_db, client, get_valid_token):
    """Test successful user deletion"""
    mock_delete_user_db.return_value = True
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/user/deleteuser?id=1")

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    print(json_data)
    assert json_data["success"] == True
    assert json_data["message"] == "User deleted successfully."


def test_delete_user_missing_id(client, get_valid_token):
    """Test user deletion with missing id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/user/deleteuser")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_user_invalid_id(client, get_valid_token):
    """Test user deletion with non-integer id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/user/deleteuser?id=abc")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_non_existent_id(mock_delete_user_db, client, get_valid_token):
    """Test user deletion with non-existent id"""
    mock_delete_user_db.return_value = False
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/user/deleteuser?id=99999")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "User deletion failed."


@patch("dao.v1.user_dao.user_databaseConnection.deleteUserDB")
def test_delete_user_unexpected_error(mock_delete_user_db, client, get_valid_token):
    """Test user deletion with unexpected error"""
    mock_delete_user_db.side_effect = Exception("Database error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/user/deleteuser?id=1")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] == False
    assert json_data["message"] == "Database error"


# INTEGRATION TEST ENDED
# * DELETE USER ENDED
