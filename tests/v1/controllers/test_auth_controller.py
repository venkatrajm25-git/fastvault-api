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
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from controllers.v1.auth_controller import Authenticator
from model.v1.user_model import Users
from routes.v1 import auth_route


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../../"))

# * SHOW REGISTER FORM STARTED


def test_show_register_form_success(client):
    """Test successful rendering of register.html for GET request"""
    response = client.get("/v1/auth/createuser")

    assert response.status_code == HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


@patch("controllers.v1.auth_controller.templates.TemplateResponse")
def test_show_register_form_template_context(mock_template_response, client):
    """Test that the template is called with correct context"""
    mock_template_response.return_value = "Mocked HTML Response"
    response = client.get("/v1/auth/createuser")

    assert response.status_code == HTTP_200_OK
    mock_template_response.assert_called_once()


# * SHOW REGISTER FORM ENDED


# * CREATE USER FUNCTION STARTED
@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_success(mock_serv, client, get_valid_token):
    """Test successful user creation"""
    mock_serv.return_value = JSONResponse(
        content={
            "message": "User registered successfully.",
            "data": {
                "email": "test@jeenox.com",
                "username": "testuser",
                "status": 1,
                "role": 2,
            },
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)
    print("response", response.text)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["message"] == "User registered successfully."
    assert json_data["data"]["email"] == "test@jeenox.com"
    assert json_data["data"]["username"] == "testuser"
    assert json_data["data"]["status"] == 1
    assert json_data["data"]["role"] == 2


def test_create_user_missing_email(client, get_valid_token):
    """Test user creation with missing email"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"password": "Test@123", "username": "testuser", "status": 1, "role": 2}
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Email is required"


def test_create_user_missing_password(client, get_valid_token):
    """Test user creation with missing password"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Password is required"


@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_email_already_exists(mock_serv, client, get_valid_token):
    """Test user creation with already registered email"""
    mock_serv.return_value = JSONResponse(
        content={"status": "false", "message": "Email ID is already registered."},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Email ID is already registered."


@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_invalid_status(mock_serv, client, get_valid_token):
    """Test user creation with invalid status"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": "invalid",  # Invalid status
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_duplicate_entry(mock_serv, client, get_valid_token):
    """Test user creation with duplicate entry error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_foreign_key_error(mock_serv, client, get_valid_token):
    """Test user creation with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


@patch("controllers.v1.auth_controller.Auth_Serv.createUser_Serv")
def test_create_user_unexpected_error(mock_serv, client, get_valid_token):
    """Test user creation with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


def test_create_user_invalid_token(client):
    """Test user creation with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    payload = {
        "email": "test@jeenox.com",
        "password": "Test@123",
        "username": "testuser",
        "status": 1,
        "role": 2,
    }
    response = client.post("/v1/auth/createuser", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# * CREATE USER FUNCTION ENDED

# * SHOW LOGIN FORM STARTED


def test_show_login_form_success(client):
    """Test successful rendering of login.html for GET request"""
    response = client.get("/v1/auth/login")

    assert response.status_code == HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


@patch("controllers.v1.auth_controller.templates.TemplateResponse")
def test_show_login_form_template_context(mock_template_response, client):
    """Test that the template is called with correct context"""
    mock_template_response.return_value = "Mocked HTML Response"
    response = client.get("/v1/auth/login")

    assert response.status_code == HTTP_200_OK
    mock_template_response.assert_called_once()


# * SHOW LOGIN FORM ENDED


# * LOGIN STARTED
def test_login_missing_email(client):
    response = client.post("/v1/auth/login", json={"password": "admin@123"})
    assert response.status_code == 400
    assert response.json().get("message") == "Email is required"


def test_login_missing_password(client):
    response = client.post("/v1/auth/login", json={"email": "admin@velaninfo.com"})
    assert response.status_code == 400
    assert response.json().get("message") == "Password is required"


@patch("controllers.v1.auth_controller.Authenticator.login")
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


@patch("controllers.v1.auth_controller.Authenticator.login")
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
    "controllers.v1.auth_controller.Authenticator.login"
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


@patch("controllers.v1.auth_controller.Auth_Serv.login_Serv")
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
def test_forget_password_get_request(client):
    """Test GET request to forget password page."""
    response = client.get("/v1/auth/forget_password")  # Adjust URL if needed
    assert response.status_code == 200
    # print("hi bro----",response.text)

    assert "Forget Password" in response.text  # Ensure the correct template is loaded


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
    assert "Password reset link sent!" in response.text


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

# # INTEGRATION TEST STARTED


def test_send_mail_for_forget_pass(db_session):
    from utils.v1.utility import sendResetLink
    from fastapi import BackgroundTasks

    background_task = BackgroundTasks()
    receiver = "venkatraj.dev@velaninfo.com"
    success = sendResetLink(receiver, background_task, db_session)
    print("success ", success)
    assert success, "Mail sent successfully ✅"


# # INTEGRATION TEST ENDED

# * FORGET PASSWORD ENDED

# #* RESET PASSWORD STARTED


@patch("controllers.v1.auth_controller.templates.TemplateResponse")
def test_reset_password_form_exception(mock_template_response):
    # Arrange
    request = MagicMock()
    request.query_params.get.return_value = "123"
    mock_template_response.side_effect = Exception("Template not found")

    # Act
    result = Authenticator.resetPasswordForm(request)

    # Assert
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    response_data = json.loads(result.body.decode("utf-8"))
    assert response_data == {"message": "Template not found"}


def test_reset_password_form_get(client):
    """Test GET request to reset password page with userID."""
    user_id = "1"  # Example user ID
    response = client.get(
        f"/v1/auth/reset-password?userID={user_id}"
    )  # Sending request with userID
    assert response.status_code == 200
    print("-----", response.text)
    assert "Reset Password" in response.text


def test_reset_password_missing_password(client):
    response = client.post(
        "/v1/auth/reseting-password", json={"newPassword": "admin@123"}
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_reset_password_form_post_confPass(client):
    response = client.post(
        "/v1/auth/reseting-password",
        json={"newPassword": "admin@123", "confirmPassword": "admins@123", "userID": 1},
    )
    assert response.status_code == 400
    assert response.json().get("message") == "Passwords do not match. Try again."


def test_reset_password_success(client):
    response = client.post(
        "/v1/auth/reseting-password",
        json={"newPassword": "admin@123", "confirmPassword": "admin@123", "userID": 1},
    )
    assert response.status_code == 201


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

    assert response.status_code == HTTP_403_FORBIDDEN


@patch("controllers.v1.auth_controller.jwt.decode")
def test_logout_missing_email_in_token(mock_jwt_decode, client, get_valid_token):
    """Test logout with token missing email"""
    mock_jwt_decode.return_value = {}
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post("/v1/auth/logout", headers=headers)

    assert response.status_code == HTTP_401_UNAUTHORIZED
    json_data = response.json()


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
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Refresh token missing"


@patch("routes.v1.auth_route.jwt.decode")
@patch("routes.v1.auth_route.getDBConnection")
def test_refresh_token_invalid_token(mock_get_db, mock_jwt_decode, client):
    """Test invalid JWT structure"""
    mock_get_db.return_value = MagicMock()
    mock_jwt_decode.return_value = {}

    response = client.post("/v1/auth/refresh", json={"refresh_token": "some_token"})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid refresh token"


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
    assert response.json()["detail"] == "Invalid or revoked refresh token"


@patch("routes.v1.auth_route.jwt.decode", side_effect=jwt.ExpiredSignatureError)
def test_refresh_token_expired(mock_jwt_decode, client):
    """Test expired refresh token"""
    response = client.post("/v1/auth/refresh", json={"refresh_token": "expired_token"})
    assert response.status_code == HTTP_401_UNAUTHORIZED

    assert response.json()["detail"] == "Refresh token expired"


@patch("controllers.v1.auth_controller.jwt.decode", side_effect=jwt.InvalidTokenError)
def test_refresh_token_invalid_signature(mock_jwt_decode, client):
    """Test invalid refresh token"""
    response = client.post("/v1/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"


class FakeUser:
    def __init__(self, id, email, is_deleted, refresh_token):
        self.id = id
        self.email = email
        self.is_deleted = is_deleted
        self.refresh_token = refresh_token
        self.access_token = None


# * REFRESH TOKEN ENDED

# from database.v1.connection import getDBConnection
# from model.v1.user_model import Users
# from datetime import datetime, timedelta, timezone


# # def override_get_db():
# #     mock_session = MagicMock()
# #     mock_user = MagicMock(spec=Users)
# #     mock_user.email = "test@jeenox.com"
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
#     refresh_token = create_test_refresh_token(user_id=1, email="test@jeenox.com")

#     # Override the getDBConnection dependency
#     def override_get_db():
#         mock_session = MagicMock()
#         mock_user = MagicMock(spec=Users)
#         mock_user.id = 1
#         mock_user.email = "test@jeenox.com"
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
#     refresh_token = create_test_refresh_token(user_id=1, email="test@jeenox.com")

#     # Mock JWT decode to return the expected payload
#     mock_jwt_decode.return_value = {"user_id": 1, "email": "test@jeenox.com"}

#     # Mock user from DB
#     mock_user = MagicMock(spec=Users)
#     mock_user.email = "test@jeenox.com"
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
