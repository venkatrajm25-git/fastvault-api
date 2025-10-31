import pytest
from fastapi.responses import JSONResponse
from unittest.mock import patch, MagicMock
import json
from dao.v1.user_dao import user_databaseConnection
from utils.v1.utility import (
    deleteFile,
    deletewithFilename,
    saveImage,
    sendEmail_background_task,
    sendResetLink,
)


@pytest.fixture
def mock_smtp():
    return MagicMock()


def test_send_email_exception(mock_smtp):
    # Arrange
    receiver = "recipient@example.com"
    message = "Test email message"

    with patch("utils.v1.utility.smtplib.SMTP", return_value=mock_smtp):
        # Simulate an exception in any SMTP operation
        mock_smtp.starttls.side_effect = Exception("SMTP connection error")

        # Act
        response = sendEmail_background_task(receiver, message)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "SMTP connection error"


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_background_task():
    return MagicMock()


def test_send_reset_link_exception(mock_db_session, mock_background_task):
    # Arrange
    receiver = "test@example.com"

    with patch(
        "utils.v1.utility.user_databaseConnection.getUserTable",
        side_effect=Exception("Database connection error"),
    ):
        # Act
        result = sendResetLink(receiver, mock_background_task, mock_db_session)

    # Assert
    assert result is False
    mock_background_task.add_task.assert_not_called()


def test_send_reset_link_exception(mock_db_session, mock_background_task):
    # Arrange
    receiver = "test@example.com"

    with patch(
        "dao.v1.user_dao.user_databaseConnection.getUserTable",
        side_effect=Exception("Database connection error"),
    ):
        # Act
        result = sendResetLink(receiver, mock_background_task, mock_db_session)

    # Assert
    assert result is False
    mock_background_task.add_task.assert_not_called()


def test_save_image_exception():
    # Arrange
    image = MagicMock()
    image.filename = "test.jpg"

    with patch("os.path.join", return_value="/uploads/test.jpg"):
        with patch.object(image, "save", side_effect=OSError("Disk full")):
            # Act
            try:
                saveImage(image)
                pytest.fail("Expected OSError")
            except OSError as e:
                # Assert
                assert str(e) == "Disk full"


def test_delete_file_exception():
    # Arrange
    image = MagicMock()
    image.filename = "test.jpg"

    with patch("os.path.join", return_value="/uploads/test.jpg"):
        with patch("os.remove", side_effect=FileNotFoundError("File not found")):
            # Act
            result = deleteFile(image)

    # Assert
    assert result is None  # Function returns None implicitly


def test_delete_with_filename_exception():
    # Arrange
    image = "test.jpg"

    with patch("os.path.join", return_value="/uploads/test.jpg"):
        with patch("os.remove", side_effect=FileNotFoundError("File not found")):
            # Act
            result = deletewithFilename(image)

    # Assert
    assert result is None  # Function returns None implicitly
