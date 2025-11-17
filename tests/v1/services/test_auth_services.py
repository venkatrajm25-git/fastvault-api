import pytest
from unittest.mock import MagicMock, patch
from fastapi.responses import JSONResponse
from http import HTTPStatus
import json
from helpers.v1.helpers import IDGeneration
from services.v1.auth_services import AuthServices  # Adjust import path
from model.v1.user_model import User  # Adjust import


@pytest.fixture
def mock_db_session():
    return MagicMock()


import asyncio


def test_create_user_success(mock_db_session):
    asyncio.run(
        _test_create_user_success(mock_db_session)
    )  # 👈 wrap with asyncio.run()


async def _test_create_user_success(mock_db_session):  # 👈 move logic to async function
    # Arrange
    data_list = ["test@example.com", "password123", "testuser", 1, 1]
    accept_language = "en"
    current_user = {"user_id": "admin@example.com"}

    # Mock database query to return None (no existing user)
    mock_db_session.query().filter().first.return_value = None

    # Mock IDGeneration.userID
    with patch("services.v1.AuthServices.IDGeneration.userID", return_value="22"):
        # Mock bcrypt.hashpw
        with patch(
            "services.v1.AuthServices.bcrypt.hashpw",
            return_value=b"hashed_password",
        ):
            # Mock user_databaseConnection.registerUserDetails
            mock_response = JSONResponse(
                content={"message": "User registered"}, status_code=201
            )

            # Act
            response = await AuthServices.createUser_Serv(
                data_list, mock_db_session, accept_language, current_user
            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    print(response_data)
    assert response_data["message"] == "User registered successfully."
    assert response_data["data"] == {
        "email": "test@example.com",
        "username": "testuser",
        "status": 1,
        "role": 1,
    }


def test_create_user_duplicate_email(mock_db_session):
    data_list = ["test@example.com", "password123", "testuser", 1, 1]
    accept_language = "en"
    current_user = {"user_id": "admin@example.com"}

    mock_user = MagicMock()
    mock_user.is_deleted = 0
    mock_db_session.query().filter().first.return_value = mock_user

    with patch(
        "services.v1.AuthServices.translate_pair", return_value={"status": "false"}
    ), patch(
        "services.v1.AuthServices.translate_many",
        return_value="Email already exists",
    ):

        response = asyncio.run(
            AuthServices.createUser_Serv(
                data_list, mock_db_session, accept_language, current_user
            )
        )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode())
    assert response_data["status"] == "false"
    assert response_data["message"] == "Email already exists"


def test_create_user_database_failure(mock_db_session):
    data_list = ["test@example.com", "password123", "testuser", 1, 1]
    accept_language = "en"
    current_user = {"user_id": "admin@example.com"}

    mock_db_session.query().filter().first.return_value = None

    with patch(
        "services.v1.AuthServices.IDGeneration.userID", return_value="22"
    ), patch(
        "services.v1.AuthServices.bcrypt.hashpw", return_value=b"hashed_password"
    ), patch(
        "services.v1.AuthServices.user_databaseConnection.registerUserDetails",
        return_value=JSONResponse(content={"error": "Database error"}, status_code=400),
    ):

        response = asyncio.run(
            AuthServices.createUser_Serv(
                data_list, mock_db_session, accept_language, current_user
            )
        )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode())
    assert response_data["error"] == "Database error"


def test_create_user_general_exception(mock_db_session):
    data_list = ["test@example.com", "password123", "testuser", 1, 1]
    accept_language = "en"
    current_user = {"user_id": "admin@example.com"}

    mock_db_session.query().filter().first.side_effect = Exception("Unexpected error")

    with patch(
        "services.v1.AuthServices.translate",
        return_value="An internal error occurred. Please try again later.",
    ):

        response = asyncio.run(
            AuthServices.createUser_Serv(
                data_list, mock_db_session, accept_language, current_user
            )
        )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = json.loads(response.body.decode())
    assert (
        response_data["error"] == "An internal error occurred. Please try again later."
    )
    assert response_data["detail"] == "Unexpected error"


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_request():
    return MagicMock()


def test_login_success(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "password123"
    accept_language = "en"

    # Mock user query
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.pwd = "hashed_password"
    mock_db_session.query().filter().first.return_value = mock_user

    # Mock dependencies
    with patch(
        "services.v1.AuthServices.Auth_DatabaseConnection.verifyActiveStatus",
        return_value=1,
    ):
        with patch("services.v1.AuthServices.bcrypt.checkpw", return_value=True):
            with patch(
                "services.v1.AuthServices.create_access_token",
                return_value="access_token_123",
            ):
                with patch(
                    "services.v1.AuthServices.create_refresh_token",
                    return_value="refresh_token_123",
                ):
                    with patch("services.v1.AuthServices.log_audit", return_value=None):
                        with patch(
                            "services.v1.AuthServices.Auth_DatabaseConnection.updateAccessToken",
                            return_value=None,
                        ):
                            # Act
                            response = asyncio.run(
                                AuthServices.login_Serv(
                                    email,
                                    password,
                                    mock_db_session,
                                    accept_language,
                                    mock_request,
                                )
                            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["message"] == "Login successful"
    assert response_data["access_token"] == "access_token_123"
    assert response_data["refresh_token"] == "refresh_token_123"
    assert response_data["login id"] == "test@example.com"


def test_login_user_not_found(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "password123"
    accept_language = "en"

    # Mock user query to return None
    mock_db_session.query().filter().first.return_value = None

    # Act
    response = asyncio.run(
        AuthServices.login_Serv(
            email, password, mock_db_session, accept_language, mock_request
        )
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    response_data = json.loads(response.body.decode("utf-8"))
    print(response_data)
    assert response_data["success"] == "false"
    assert response_data["message"] == "User not found."


def test_login_inactive_role(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "password123"
    accept_language = "en"

    # Mock user query
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.pwd = "hashed_password"
    mock_db_session.query().filter().first.return_value = mock_user

    # Mock verifyActiveStatus to return inactive status (2)
    with patch(
        "services.v1.AuthServices.Auth_DatabaseConnection.verifyActiveStatus",
        return_value=2,
    ):
        # Act
        response = asyncio.run(
            AuthServices.login_Serv(
                email, password, mock_db_session, accept_language, mock_request
            )
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] == "false"
    assert response_data["message"] == "Login failed. Role is not active."


def test_login_incorrect_password(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "wrong_password"
    accept_language = "en"

    # Mock user query
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.pwd = "hashed_password"
    mock_db_session.query().filter().first.return_value = mock_user

    # Mock verifyActiveStatus
    with patch(
        "services.v1.AuthServices.Auth_DatabaseConnection.verifyActiveStatus",
        return_value=1,
    ):
        # Mock bcrypt.checkpw to return False
        with patch("services.v1.AuthServices.bcrypt.checkpw", return_value=False):
            # Act
            response = asyncio.run(
                AuthServices.login_Serv(
                    email, password, mock_db_session, accept_language, mock_request
                )
            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["message"] == "New user? Click here to /register"


def test_login_no_stored_password(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "password123"
    accept_language = "en"

    # Mock user query with empty password
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.pwd = ""
    mock_db_session.query().filter().first.return_value = mock_user

    # Act
    response = asyncio.run(
        AuthServices.login_Serv(
            email, password, mock_db_session, accept_language, mock_request
        )
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    print(response_data)
    assert response_data["error"] == "Invalid email or password. Try again."
    assert response_data["message"] == "New user? Click here to /register"


def test_login_audit_log_exception(mock_db_session, mock_request):
    # Arrange
    email = "test@example.com"
    password = "password123"
    accept_language = "en"

    # Mock user query
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.pwd = "hashed_password"
    mock_db_session.query().filter().first.return_value = mock_user

    # Mock dependencies
    with patch(
        "services.v1.AuthServices.Auth_DatabaseConnection.verifyActiveStatus",
        return_value=1,
    ):
        with patch("services.v1.AuthServices.bcrypt.checkpw", return_value=True):
            with patch(
                "services.v1.AuthServices.create_access_token",
                return_value="access_token_123",
            ):
                with patch(
                    "services.v1.AuthServices.create_refresh_token",
                    return_value="refresh_token_123",
                ):
                    with patch(
                        "services.v1.AuthServices.log_audit",
                        side_effect=Exception("Audit log error"),
                    ):
                        with patch(
                            "services.v1.AuthServices.Auth_DatabaseConnection.updateAccessToken",
                            return_value=None,
                        ):
                            # Act
                            response = asyncio.run(
                                AuthServices.login_Serv(
                                    email,
                                    password,
                                    mock_db_session,
                                    accept_language,
                                    mock_request,
                                )
                            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["message"] == "Login successful"
    assert response_data["access_token"] == "access_token_123"
    assert response_data["refresh_token"] == "refresh_token_123"
    assert response_data["login id"] == "test@example.com"
