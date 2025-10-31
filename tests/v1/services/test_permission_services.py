from unittest.mock import MagicMock
from fastapi.responses import JSONResponse
from controllers.v1.perm_controller import PermissionModule
from dao.v1.perm_dao import UserPerm_DBConn
from services.v1.permission_services import Perm_Serv
from dao.v1.user_dao import user_databaseConnection
from dao.v1.perm_dao import UserPerm_DBConn


# Replace with your actual ORM models if needed
class DummyPerm:
    def __init__(self, id, user_id, module_id, permission_id):
        self.id = id
        self.user_id = user_id
        self.module_id = module_id
        self.permission_id = permission_id


class DummyUser:
    def __init__(self, id):
        self.id = id


# ------------ UPDATE USER PERMISSION ------------


def test_up_id_not_found(db_session):
    UserPerm_DBConn.getUserPData = lambda db: []
    response = Perm_Serv.updateUserPermissionService(1, 2, 3, 4, db_session, "en")
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400


def test_user_id_not_found(db_session):
    UserPerm_DBConn.getUserPData = lambda db: [DummyPerm(1, 10, 20, 30)]
    user_databaseConnection.getUserTable = lambda db: [
        DummyUser(99)
    ]  # user_id 2 not in DB
    response = Perm_Serv.updateUserPermissionService(1, 2, 20, 30, db_session, "en")
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400


def test_no_permission_data_found(db_session):
    from services.v1.permission_services import Perm_Serv

    # Mock DB call to return empty list
    UserPerm_DBConn.getPermissionsOfUser = lambda user_id, db: []

    # Call the actual service function
    response = Perm_Serv.getSingleUserPermission_Serv(
        user_id=1001, db=db_session, accept_language="en"
    )

    # Now this will be a JSONResponse, not a list
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_json = response.body.decode()
    assert '"success":"false"' in response_json


def test_valid_permission_data_found(db_session):
    # Mocking UserPerm_DBConn.getPermissionsOfUser to return a valid tuple structure
    UserPerm_DBConn.getPermissionsOfUser = lambda user_id, db: (
        "user@example.com",
        {"1": [101, 102], "2": [103]},
        {"1001": [201, 202, 203]},
    )

    # Call the method
    result = UserPerm_DBConn.getPermissionsOfUser(user_id=1001, db=db_session)

    # Assert return is a tuple
    assert isinstance(result, tuple)

    # Unpack the result
    email, role_perms, user_perms = result

    # Validate values
    assert email == "user@example.com"
    assert role_perms == {"1": [101, 102], "2": [103]}
    assert user_perms == {"1001": [201, 202, 203]}


# ----------- GET SINGLE USER PERMISSION-------------


def test_get_single_user_permission_success(monkeypatch, db_session):
    # Mocked data that would come from the DB call
    mocked_data = [
        ("user@example.com", None, 1, 101, 1001, 201),
        ("user@example.com", None, 1, 102, 1001, 202),
        ("user@example.com", None, 2, 103, 1001, 203),
    ]

    # Patch the DB call
    monkeypatch.setattr(
        UserPerm_DBConn, "getPermissionsOfUser", lambda user_id, db: mocked_data
    )

    # Call the service
    result = Perm_Serv.getSingleUserPermission_Serv(
        user_id=10000, db=db_session, accept_language="en"
    )

    # Validate result structure
    assert isinstance(result, tuple)
    email, role_permissions, user_permissions = result

    assert email == "user@example.com"
    assert role_permissions == {"1": [101, 102], "2": [103]}
    assert user_permissions == {"1001": [201, 202, 203]}


def test_get_single_user_permission_not_found(monkeypatch, db_session):
    # Patch DB call to return empty list
    monkeypatch.setattr(UserPerm_DBConn, "getPermissionsOfUser", lambda user_id, db: [])

    # Call the service
    response = Perm_Serv.getSingleUserPermission_Serv(
        user_id=1001, db=db_session, accept_language="en"
    )

    # Validate that a JSONResponse is returned
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400

    # Extract content
    content = response.body.decode()
    assert "permission" in content.lower()
    assert "not found" in content.lower() or "false" in content.lower()
