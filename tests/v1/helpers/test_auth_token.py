import asyncio
import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import patch, MagicMock
import json
import jwt
from middleware.v1.auth_token import token_required  # Adjust to your module path


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_credentials():
    return MagicMock(spec=HTTPAuthorizationCredentials)


def test_token_required_success_admin(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}
    permissions_data = [(None, "admin", None, None)]

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=True,
            ):
                with patch(
                    "middleware.v1.auth_token.UserPerm_DBConn.verifyPermissionsOfUser",
                    return_value=permissions_data,
                ):
                    # Act
                    verify_token = token_required()
                    result = asyncio.run(
                        verify_token(credentials=mock_credentials, db=mock_db_session)
                    )

    # Assert
    assert isinstance(result, dict)
    assert result == {
        "user_id": "user_123",
        "email": "test@example.com",
        "role": "admin",
        "permissions": set(),
        "token": "test_token",
    }


def test_token_required_success_non_admin(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}
    permissions_data = [(None, "user", "resource", "read")]
    required_role = "user"
    required_permission = [("resource", "read")]

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=True,
            ):
                with patch(
                    "middleware.v1.auth_token.UserPerm_DBConn.verifyPermissionsOfUser",
                    return_value=permissions_data,
                ):
                    # Act
                    verify_token = token_required(
                        required_role=required_role,
                        required_permission=required_permission,
                    )
                    result = asyncio.run(
                        verify_token(credentials=mock_credentials, db=mock_db_session)
                    )

    # Assert
    assert isinstance(result, dict)
    assert result == {
        "user_id": "user_123",
        "email": "test@example.com",
        "role": "user",
        "permissions": {("resource", "read")},
        "token": "test_token",
    }


def test_token_required_missing_token(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = ""

    # Act
    verify_token = token_required()
    response = asyncio.run(
        verify_token(credentials=mock_credentials, db=mock_db_session)
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 403
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["message"] == "Token is missing!"


def test_token_required_blacklisted_token(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"

    with patch("middleware.v1.auth_token.bltFunc", return_value={"test_token"}):
        # Act
        verify_token = token_required()
        try:
            asyncio.run(verify_token(credentials=mock_credentials, db=mock_db_session))
            pytest.fail("Expected HTTPException")
        except HTTPException as e:
            # Assert
            assert e.status_code == 401
            assert e.detail == {
                "message": "Invalid Token or Token revoked. Please log in again."
            }


def test_token_required_invalid_token_jwt(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch(
            "middleware.v1.auth_token.jwt.decode", side_effect=jwt.InvalidTokenError
        ):
            # Act
            verify_token = token_required()
            try:
                asyncio.run(
                    verify_token(credentials=mock_credentials, db=mock_db_session)
                )
                pytest.fail("Expected HTTPException")
            except HTTPException as e:
                # Assert
                assert e.status_code == 401
                assert e.detail == {"message": "Invalid token!"}


def test_token_required_expired_token(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch(
            "middleware.v1.auth_token.jwt.decode",
            side_effect=jwt.ExpiredSignatureError,
        ):
            # Act
            verify_token = token_required()
            try:
                asyncio.run(
                    verify_token(credentials=mock_credentials, db=mock_db_session)
                )
                pytest.fail("Expected HTTPException")
            except HTTPException as e:
                # Assert
                assert e.status_code == 401
                assert e.detail == {"message": "Token expired!"}


def test_token_required_invalid_token_validation(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=False,
            ):
                # Act
                verify_token = token_required()
                try:
                    asyncio.run(
                        verify_token(credentials=mock_credentials, db=mock_db_session)
                    )
                    pytest.fail("Expected HTTPException")
                except HTTPException as e:
                    # Assert
                    assert e.status_code == 401
                    assert e.detail == {"message": "Invalid Token!"}


def test_token_required_no_user_role(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}
    permissions_data = [(None, None, None, None)]

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=True,
            ):
                with patch(
                    "middleware.v1.auth_token.UserPerm_DBConn.verifyPermissionsOfUser",
                    return_value=permissions_data,
                ):
                    # Act
                    verify_token = token_required()
                    try:
                        asyncio.run(
                            verify_token(
                                credentials=mock_credentials, db=mock_db_session
                            )
                        )
                        pytest.fail("Expected HTTPException")
                    except HTTPException as e:
                        # Assert
                        assert e.status_code == 403
                        assert e.detail == {"message": "User role not found!"}


def test_token_required_unauthorized_role(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}
    permissions_data = [(None, "user", None, None)]
    required_role = "admin"

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=True,
            ):
                with patch(
                    "middleware.v1.auth_token.UserPerm_DBConn.verifyPermissionsOfUser",
                    return_value=permissions_data,
                ):
                    # Act
                    verify_token = token_required(required_role=required_role)
                    try:
                        asyncio.run(
                            verify_token(
                                credentials=mock_credentials, db=mock_db_session
                            )
                        )
                        pytest.fail("Expected HTTPException")
                    except HTTPException as e:
                        # Assert
                        assert e.status_code == 403
                        assert e.detail == {
                            "message": "Unauthorized! Admin access required."
                        }


def test_token_required_permission_denied(mock_db_session, mock_credentials):
    # Arrange
    mock_credentials.credentials = "Bearer test_token"
    decoded_token = {"email": "test@example.com", "user_id": "user_123"}
    permissions_data = [(None, "user", "resource", "write")]
    required_permission = [("resource", "read")]

    with patch("middleware.v1.auth_token.bltFunc", return_value=set()):
        with patch("middleware.v1.auth_token.jwt.decode", return_value=decoded_token):
            with patch(
                "middleware.v1.auth_token.Auth_DatabaseConnection.validateToken",
                return_value=True,
            ):
                with patch(
                    "middleware.v1.auth_token.UserPerm_DBConn.verifyPermissionsOfUser",
                    return_value=permissions_data,
                ):
                    # Act
                    verify_token = token_required(
                        required_permission=required_permission
                    )
                    try:
                        asyncio.run(
                            verify_token(
                                credentials=mock_credentials, db=mock_db_session
                            )
                        )
                        pytest.fail("Expected HTTPException")
                    except HTTPException as e:
                        # Assert
                        assert e.status_code == 403
                        assert e.detail == {"message": "No Access! Permission denied."}
