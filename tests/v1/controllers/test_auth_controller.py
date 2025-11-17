import json
import os, sys
from unittest.mock import patch
from fastapi.responses import JSONResponse
from unittest.mock import MagicMock
import jwt
from httpx import Auth
from pytest import Session
from main import app
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from controllers.v1.auth_controller import AuthController
from model.v1.user_model import User
from routes.v1 import auth_route


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../../"))


# * CREATE USER FUNCTION STARTED
@patch("controllers.v1.auth_controller.AuthServices.register_serv")
def test_create_user_success(mock_serv, client, get_valid_token):
    """Test successful user creation"""
    mock_serv.return_value = JSONResponse(
        content={
            "message": "User registered successfully.",
            "data": {
                "email": "test@fastvaultapi.com",
                "username": "testuser",
                "status": 1,
                "role": 2,
            },
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)
    print("response", response.text)
    assert response.status_code == HTTP_201_CREATED


def test_create_user_missing_email(client, get_valid_token):
    """Test user creation with missing email"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"password": "Test@123", "username": "testuser", "status": 1, "role": 2}
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_create_user_missing_password(client, get_valid_token):
    """Test user creation with missing password"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


@patch("controllers.v1.auth_controller.AuthServices.register_serv")
def test_create_user_email_already_exists(mock_serv, client, get_valid_token):
    """Test user creation with already registered email"""
    mock_serv.return_value = JSONResponse(
        content={"status": "false", "message": "Email ID is already registered."},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Email ID is already registered."


@patch("controllers.v1.auth_controller.AuthServices.register_serv")
def test_create_user_invalid_status(mock_serv, client, get_valid_token):
    """Test user creation with invalid status"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "password": "Test@123",
        "username": "testuser",
        "status": "invalid",  # Invalid status
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.auth_controller.AuthServices.register_serv")
def test_create_user_duplicate_entry(mock_serv, client, get_valid_token):
    """Test user creation with duplicate entry error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch("controllers.v1.auth_controller.AuthServices.register_serv")
def test_create_user_foreign_key_error(mock_serv, client, get_valid_token):
    """Test user creation with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@fastvaultapi.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/register", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


# * CREATE USER FUNCTION ENDED


# * LOGIN STARTED
def test_login_missing_email(client):
    response = client.post("/v1/auth/login", json={"password": "admin@123"})
    assert response.status_code == 422


def test_login_missing_password(client):
    response = client.post("/v1/auth/login", json={"email": "admin@velaninfo.com"})
    assert response.status_code == 422


@patch("controllers.v1.auth_controller.AuthController.login_controller")
def test_login_user_not_found(mock_login_serv, client):
    mock_login_serv.return_value = JSONResponse(
        content={"status": "false", "message": "User not found"}, status_code=404
    )

    response = client.post(
        "/v1/auth/login",
        json={"email": "unknown@velaninfo.com", "password": "admin@123"},
    )
    assert response.status_code == 404
    assert response.json().get("message") == "User not found"


@patch("controllers.v1.auth_controller.AuthController.login_controller")
def test_login_wrong_password(mock_login_serv, client):
    mock_login_serv.return_value = JSONResponse(
        content={"message": "Invalid email or password. Try again."}, status_code=404
    )

    response = client.post(
        "/v1/auth/login", json={"email": "admin@gmail.com", "password": "wrongpassword"}
    )
    assert response.status_code == 404
    assert response.json().get("message") == "Invalid email or password. Try again."


@patch(
    "controllers.v1.auth_controller.AuthController.login_controller"
)  # Mock Auth_Serv.login_Serv
def test_login_success(mock_login_serv, client):
    """Test login success."""
    # Mocking the login function to return a successful response
    mock_login_serv.return_value = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": "token",
            "refresh_token": "r_token",
            "login id": "email",
        }
    )
    # Corrected URL (added `/` at the beginning)
    response = client.post(
        "/v1/auth/login", json={"email": "admin@gmail.com", "password": "admin@123"}
    )
    # Assertions
    print("[DEBUG] - Token: ", response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()


@patch("controllers.v1.auth_controller.AuthServices.login_serv")
def test_login_unexpected_error(mock_serv, client):
    """Test add_risk_summary with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    payload = {"email": "admin@gmail.com", "password": "admin@123"}
    response = client.post("/v1/auth/login", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "unexpected error in service" in json_data["message"].lower()


# * LOGIN ENDED

# * FORGET PASSWORD STARTED


# UNIT TEST STARTED


def test_forget_password_missing_email(client):
    response = client.post("/v1/auth/forgetpassword", json={})
    assert response.status_code == 400
    assert "Enter your email" in response.text


@patch("controllers.v1.auth_controller.user_databaseConnection.getUserTable")
def test_forget_password_success(mock_getUserTable, client):
    mock_user = MagicMock()
    mock_user.email = "venkatraj.dev@velaninfo.com"
    mock_user.id = 2

    mock_getUserTable.return_value = [mock_user]
    response = client.post(
        "/v1/auth/forgetpassword", json={"email": "venkatraj.dev@velaninfo.com"}
    )

    assert response.status_code == 200
    assert "Email Sent successfully." in response.text


def test_forget_password_user_not_found(client):
    response = client.post(
        "/v1/auth/forgetpassword", json={"email": "notauser@velaninfo.com"}
    )
    assert response.status_code == 400
    assert "Email not registered." in response.text


@patch("controllers.v1.auth_controller.user_databaseConnection.getUserTable")
def test_forget_password_exception_handling(mock_send_reset_link, client):
    """Test forgetPassword raises unexpected error and returns JSON 400"""
    # Force the service to raise an unexpected exception
    mock_send_reset_link.side_effect = Exception("Unexpected error in service")

    payload = {"email": "admin@gmail.com"}
    response = client.post("/v1/auth/forgetpassword", json=payload)

    assert response.status_code == HTTP_400_BAD_REQUEST


# UNIT TEST ENDED


# #* RESET PASSWORD STARTED


def test_reset_password_missing_password(client):
    response = client.post("/v1/auth/reset-password", json={"newPassword": "admin@123"})
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# def (client):
#     response = client.post(
#         "/v1/auth/reset-password",
#         json={
#             "newPassword": "admin@123",
#             "confirmPassword": "admin@123",
#             "token": "token",
#         },
#     )
#     assert response.status_code == 201


# #* RESET PASSWORD ENDED

# * LOGOUT STARTED


def test_logout_success(client, get_valid_token):
    token = get_valid_token
    print("[DEBUG]Token: ", token)
    headers = {"Authorization": f"Bearer {token}", "Accept-Language": "en"}
    response = client.post(
        "/v1/auth/logout",
        headers=headers,
    )
    print("[DEBUG]Logout Response: ", response)
    assert response.status_code == 200
    assert response.json().get("message") == "Logged Out Successfully"


def test_logout_missing_token(client):
    """Test logout with missing token"""
    headers = {"Accept-Language": "en"}
    response = client.post("/v1/auth/logout", headers=headers)

    assert response.status_code == HTTP_401_UNAUTHORIZED


# Expected error message
# * LOGOUT END


# @pytest.fixture
# def client():
#     app.testing = True
#     with app.test_client() as client:
#         yield client


# * REFRESH TOKEN STARTED


def test_refresh_token_missing_token(client):
    """Test refresh token with missing token"""
    response = client.post("/v1/auth/refresh", json={})
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token missing"


@patch("routes.v1.auth_route.jwt.decode")
@patch("routes.v1.auth_route.getDBConnection")
def test_refresh_token_invalid_token(mock_get_db, mock_jwt_decode, client):
    """Test invalid JWT structure"""
    mock_get_db.return_value = MagicMock()
    mock_jwt_decode.return_value = {}

    response = client.post("/v1/auth/refresh", json={"refresh_token": "some_token"})
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token missing"


@patch("routes.v1.auth_route.jwt.decode")
@patch("routes.v1.auth_route.getDBConnection")
def test_refresh_token_not_found(mock_get_db, mock_jwt_decode, client):
    """Test when refresh token not found in DB"""
    mock_jwt_decode.return_value = {"email": "user@example.com"}
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_db.query().filter().first.return_value = None  # User not found

    response = client.post("/v1/auth/refresh", json={"refresh_token": "fake_token"})
    print(response.text)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token missing"


@patch("routes.v1.auth_route.jwt.decode", side_effect=jwt.ExpiredSignatureError)
def test_refresh_token_expired(mock_jwt_decode, client):
    """Test expired refresh token"""
    response = client.post("/v1/auth/refresh", json={"refresh_token": "expired_token"})
    assert response.status_code == HTTP_401_UNAUTHORIZED

    assert response.json()["detail"] == "Refresh token missing"


class FakeUser:
    def __init__(self, id, email, is_deleted, refresh_token):
        self.id = id
        self.email = email
        self.is_deleted = is_deleted
        self.refresh_token = refresh_token
        self.access_token = None


# * REFRESH TOKEN ENDED

# from database.v1.connection import getDBConnection
# from model.v1.user_model import User
# from datetime import datetime, timedelta, timezone


# # def override_get_db():
# #     mock_session = MagicMock()
# #     mock_user = MagicMock(spec=User)
# #     mock_user.email = "test@fastvaultapi.com"
# #     mock_user.id = 1
# #     mock_user.refresh_token = "your_token"  # will override below
# #     mock_user.is_deleted = 0

# #     mock_session.query.return_value.filter.return_value.first.return_value = mock_user
# #     return mock_session


# # app.dependency_overrides[getDBConnection] = override_get_db


# def create_test_refresh_token(user_id: int, email: str) -> str:
#     payload = {
#         "user_id": user_id,
#         "email": email,
#         "exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
#     }
#     return jwt.encode(payload, "test-secret-key", algorithm="HS256")


# def test_refresh_token_success2(client):
#     # Create a valid refresh token (simulate how your system generates it)
#     refresh_token = create_test_refresh_token(user_id=1, email="test@fastvaultapi.com")

#     # Override the getDBConnection dependency
#     def override_get_db():
#         mock_session = MagicMock()
#         mock_user = MagicMock(spec=User)
#         mock_user.id = 1
#         mock_user.email = "test@fastvaultapi.com"
#         mock_user.refresh_token = refresh_token
#         mock_user.is_deleted = 0

#         # Mock query().filter().first() chain to return mock_user
#         mock_session.query.return_value.filter.return_value.first.return_value = (
#             mock_user
#         )
#         return mock_session

#     app.dependency_overrides[getDBConnection] = override_get_db

#     # Call the refresh token endpoint
#     response = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})

#     # Output and assertion
#     print("Status Code:", response.status_code)
#     print("Response:", response.json())
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert "refresh_token" in response.json()

#     # Clean up
#     app.dependency_overrides = {}


# @patch("routes.v1.auth_route.jwt.decode")
# @patch("routes.v1.auth_route.create_access_token")
# @patch("routes.v1.auth_route.create_refresh_token")
# @patch("routes.v1.auth_route.getDBConnection")
# def test_refresh_token_success(
#     mock_db, mock_create_refresh, mock_create_access, mock_jwt_decode, client
# ):
#     """Test successful refresh token flow with generated token"""
#     # Generate a test refresh token
#     refresh_token = create_test_refresh_token(user_id=1, email="test@fastvaultapi.com")

#     # Mock JWT decode to return the expected payload
#     mock_jwt_decode.return_value = {"user_id": 1, "email": "test@fastvaultapi.com"}

#     # Mock user from DB
#     mock_user = MagicMock(spec=User)
#     mock_user.email = "test@fastvaultapi.com"
#     mock_user.id = 1
#     mock_user.refresh_token = refresh_token
#     mock_user.is_deleted = 0

#     # Mock DB session
#     mock_session = MagicMock()
#     mock_query = mock_session.query.return_value
#     mock_filter = mock_query.filter.return_value
#     mock_filter.first.return_value = mock_user
#     mock_db.return_value.__enter__.return_value = mock_session

#     # Mock token creation
#     mock_create_access.return_value = "new_access_token"
#     mock_create_refresh.return_value = "new_refresh_token"

#     # Send request without Authorization header to avoid middleware issues
#     payload = {"refresh_token": refresh_token}
#     response = client.post("/v1/auth/refresh", json=payload)

#     # Debug output
#     print(f"Refresh token: {refresh_token}")
#     print(f"JWT decode called: {mock_jwt_decode.called}")
#     print(f"DB session called: {mock_db.called}")
#     print(f"DB query result: {mock_filter.first.return_value}")
#     print(f"Response status: {response.status_code}")
#     print(f"Response body: {response.json()}")

#     # Assertions
#     assert (
#         response.status_code == HTTP_200_OK
#     ), f"Expected 200, got {response.status_code}: {response.json()}"
#     json_data = response.json()
#     assert json_data["access_token"] == "new_access_token"
#     assert json_data["refresh_token"] == "new_refresh_token"
#     assert mock_session.commit.called, "DB commit was not called"
#     assert mock_jwt_decode.called, "JWT decode was not called"
#     assert mock_db.called, "DB connection was not called"
