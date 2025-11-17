import asyncio
import pytest
from fastapi.responses import JSONResponse
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from dao.v1.role_dao import Role_DBConn
from services.v1 import role_services
from services.v1.role_services import Role_Services  # Adjust to your module path


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_get_role_serv_all_roles():
    # Arrange
    mock_db = MagicMock()
    fake_row = MagicMock(
        id=1,
        rolename="Admin",
        status=True,
        created_by=1,
        modified_by=2,
        created_at=None,
        modifed_at=None,
    )
    with patch(
        "services.v1.role_services.Role_DBConn.getRoleData", return_value=[fake_row]
    ), patch("services.v1.role_services.translate", side_effect=lambda k, lang=None: k):

        # Act
        response: JSONResponse = asyncio.run(
            Role_Services.getRole_serv(role_id=None, db=mock_db, accept_language="en")
        )

        # Assert
        assert response.status_code == 200
        assert "roles" in response.body.decode()


# def test_get_role_serv_by_id():
#     # Arrange
#     mock_db = MagicMock()
#     fake_row = MagicMock(
#         id=1,
#         rolename="Manager",
#         status=1,
#         created_by=1,
#         modified_by=2,
#         created_at=None,
#         modifed_at=None,
#     )

#     with patch(
#         "services.v1.role_services.Role_DBConn.getRoleData", return_value=[fake_row]
#     ), patch(
#         "services.v1.role_services.translate", side_effect=lambda k, lang=None: k
#     ), patch(
#         "services.v1.role_services.verifyRoleID",
#         return_value=MagicMock(status_code=200),
#     ):

#         # Act
#         response: JSONResponse = asyncio.run(
#             Role_Services.getRole_serv(role_id=1, db=mock_db, accept_language="en")
#         )

#         # Assert
#         assert response.status_code == 200
#         assert "roles" in response.body.decode()


def test_update_role_not_found(db_session):
    # db = next(get_db())  # Get actual DB session
    invalid_role_id = 999999  # A role ID that doesn't exist
    dataList = [invalid_role_id, "TestRole", 1, 1]
    accept_language = "en"

    response = asyncio.run(Role_Services.updateRole_serv(dataList, db_session))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body is not None
    # assert b"Role not found." in response.body.lower()
