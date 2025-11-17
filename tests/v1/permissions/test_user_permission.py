import asyncio
import json
from unittest.mock import MagicMock, patch
from controllers.v1.perm_controller import PermissionModule
from dao.v1.user_dao import user_databaseConnection
from dao.v1.perm_dao import UserPerm_DBConn
from fastapi.responses import JSONResponse
from helpers.v1.permission_helpers import verifyModuleUserndPermID
from main import app
from model.v1.permission_model import UserPermission
from sqlalchemy import and_
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from services.v1 import permission_services


# * GET SINGLE USER PERMISSION STARTED


def test_get_single_user_perm_missing_both_fields(client, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getsingleuserperm", params={})
    assert response.status_code == 400
    assert "must be filled out." in response.json()["message"].lower()


def test_get_single_user_perm_user_not_found(monkeypatch, client, get_valid_token):
    def mock_get_user_table(_):
        class FakeUser:
            def __init__(self, email):
                self.email = email

        return [FakeUser("someone@else.com")]

    monkeypatch.setattr(
        "controllers.v1.perm_controller.user_databaseConnection.getUserTable",
        mock_get_user_table,
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get(
        "/v1/perm/getsingleuserperm",
        headers=headers,
        params={"email": "notfound@example.com"},
    )
    assert response.status_code == 400
    assert "not found" in response.json()["message"].lower()


def test_get_single_user_perm_by_email_success(monkeypatch, client, get_valid_token):
    class FakeUser:
        def __init__(self, id, email):
            self.id = id
            self.email = email

    monkeypatch.setattr(
        "controllers.v1.perm_controller.user_databaseConnection.getUserTable",
        lambda db: [FakeUser(101, "abc@example.com")],
    )

    def mock_perm_service(uid, db, lang):
        return ("abc@example.com", [{"mod": "m1"}], [{"perm": "p1"}])

    monkeypatch.setattr(
        "controllers.v1.perm_controller.Perm_Serv.getSingleUserPermission_Serv",
        mock_perm_service,
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get(
        "/v1/perm/getsingleuserperm",
        headers=headers,
        params={"email": "abc@example.com"},
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["user id"] == 101
    assert json_data["data"]["email id"] == "abc@example.com"


def test_get_single_user_perm_by_user_id_failed_in_service(
    monkeypatch, client, get_valid_token
):
    def mock_perm_service(uid, db, lang):
        return JSONResponse(content={"message": "Error from service"}, status_code=400)

    monkeypatch.setattr(
        "controllers.v1.perm_controller.Perm_Serv.getSingleUserPermission_Serv",
        mock_perm_service,
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getsingleuserperm", params={"user_id": 102})
    assert response.status_code == 400
    assert response.json()["message"] == "Error from service"


def test_get_single_user_perm_raises_exception(monkeypatch, client, get_valid_token):
    def broken_service(*args, **kwargs):
        raise Exception("Something went wrong")

    monkeypatch.setattr(
        "controllers.v1.perm_controller.Perm_Serv.getSingleUserPermission_Serv",
        broken_service,
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getsingleuserperm", params={"user_id": 103})
    assert response.status_code == 400
    assert "Something went wrong" in response.json()["message"]


# * GET SINGLE USER PERMISSION ENDED

# * GET ALL USER PERMISSION STARTED
# UNIT TEST STARTED


def test_get_user_permissions_all_success(client, db_session, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getuserpermission")
    res = response.json()
    assert response.status_code == 200
    assert "successfully" in res["message"].lower()


def test_get_user_permissions_with_valid_user_id(client, db_session, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # Insert test data with is_deleted=0
    UserPermissionData = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1, is_deleted=0)
        .first()
    )

    if not UserPermissionData:
        test_perm = UserPermission(
            user_id=1, module_id=1, permission_id=1, is_deleted=0
        )
        db_session.add(test_perm)
        db_session.commit()

    response = client.get("/v1/perm/getuserpermission?user_id=1")
    res = response.json()
    print(res)
    assert response.status_code == 200
    assert "successfully" in res["message"].lower()


def test_get_user_permissions_user_id_not_found(client, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getuserpermission?user_id=99999")
    res = response.json()
    assert response.status_code == 200

    assert "No user permissions." in response.text


def test_get_user_permissions_exception(client, monkeypatch, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    def mock_exception(*args, **kwargs):
        raise Exception("mocked error")

    from dao.v1.perm_dao import UserPerm_DBConn

    monkeypatch.setattr(UserPerm_DBConn, "getUserPData", mock_exception)

    response = client.get("/v1/perm/getuserpermission")
    res = response.json()
    print("resopnse", res)
    assert response.status_code == 400
    assert res["message"].lower() == "mocked error"
    assert res["success"] is False


# UNIT TEST END
# * GET ALL USER PERMISSION ENDED

# * ADD USER PERMISSION STARTED
# UNIT TEST STARTED


def test_add_user_perm_missing_fields(client, get_valid_token):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # One or more fields empty
    payload = {"user_id": "", "module_id": "", "permission_id": ""}

    response = client.post(
        "/v1/perm/adduserpermission",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 400
    assert "must" in response.json()["message"].lower()


@patch("controllers.v1.perm_controller.PermissionModule.addUserPermission")
def test_add_user_perm_user_id_not_available(mock_serv, client, get_valid_token):
    mock_serv.return_value = JSONResponse(
        content={"message": "User id not available."}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/adduserpermission",
        json={"user_id": 99999, "module_id": 1, "permission_id": 1},
        headers=headers,
    )

    assert response.status_code == 400
    assert "user id not available" in response.json()["message"].lower()


# @patch("controllers.v1.perm_controller.PermissionModule.addUserPermission")
def test_add_user_perm_module_id_not_available(client, get_valid_token):
    # mock_serv.return_value = JSONResponse(
    #     content={"message": "Module id not available."}, status_code=400
    # )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/adduserpermission",
        json={"user_id": 1, "module_id": 99999, "permission_id": 1},
        headers=headers,
    )

    assert response.status_code == 400
    assert "module id is not available." in response.json()["message"].lower()


# @patch("controllers.v1.perm_controller.PermissionModule.addUserPermission")
def test_add_user_perm_permission_id_not_available(client, get_valid_token):
    # mock_serv.return_value = JSONResponse(
    #     content={"message": "Permission ID is not available."}, status_code=400
    # )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/adduserpermission",
        json={"user_id": 1, "module_id": 1, "permission_id": 99999},
        headers=headers,
    )

    assert response.status_code == 400
    assert "permission id is not available." in response.json()["message"].lower()


@patch("controllers.v1.perm_controller.PermissionModule.addUserPermission")
def test_add_user_perm_already_exists(mock_serv, client, get_valid_token):
    mock_serv.return_value = JSONResponse(
        content={"message": "Already user permission is available."}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/adduserpermission",
        json={"user_id": 1, "module_id": 1, "permission_id": 1},
        headers=headers,
    )

    assert response.status_code == 400
    assert "already" in response.json()["message"].lower()


@patch("helpers.v1.permission_helpers.user_databaseConnection.getUserTable")
@patch("helpers.v1.permission_helpers.Module_DBConn.getModuleData")
@patch("helpers.v1.permission_helpers.Permissions_DBConn.getPermissionData")
def test_verify_module_user_perm_id_success(
    mock_get_permission_data,
    mock_get_module_data,
    mock_get_user_table,
    db_session,
):
    # Arrange
    user_id = 1
    module_id = 2
    permission_id = 3
    accept_language = "en"
    user = MagicMock(id=1)
    module = MagicMock(id=2)
    permission = MagicMock(id=3)

    mock_get_user_table.return_value = [user]
    mock_get_module_data.return_value = [module]
    mock_get_permission_data.return_value = [permission]

    # Act
    response = asyncio.run(
        verifyModuleUserndPermID(
            user_id, module_id, permission_id, db_session, accept_language
        )
    )

    # Assert
    assert response.status_code == 200
    body = json.loads(response.body.decode())
    assert "Module User and Permission ID Verified" in body["message"]
    assert "success" in body
    assert body["success"] == "true"


@patch("controllers.v1.perm_controller.PermissionModule.addUserPermission")
def test_add_user_perm_server_crash(mock_serv, client, get_valid_token):
    mock_serv.return_value = JSONResponse(
        content={"message": "Internal Server Error"}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.post(
        "/v1/perm/adduserpermission",
        json={"user_id": "1", "module_id": "1", "permission_id": "1"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "internal" in response.json()["message"].lower()


def test_add_user_permission_success_and_cleanup(client, db_session, get_valid_token):
    # Ensure no existing record
    db_session.query(UserPermission).filter_by(
        user_id=1, module_id=1, permission_id=1
    ).delete()
    db_session.commit()

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"user_id": 1, "module_id": 1, "permission_id": 1}

    response = client.post("/v1/perm/adduserpermission", json=payload)
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()

    # Validate in DB
    new_perm = (
        db_session.query(UserPermission)
        .filter_by(user_id=1, module_id=1, permission_id=1)
        .first()
    )
    assert new_perm is not None

    # Cleanup
    db_session.delete(new_perm)
    db_session.commit()


@patch("controllers.v1.perm_controller.UserPerm_DBConn.addUserPerm")
def test_add_user_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"user_id": "1", "module_id": "1", "permission_id": "1"}
    response = client.post("/v1/perm/adduserpermission", json=payload)
    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED
# * ADD USER PERMISSION ENDED


# * UPDATE USER PERMISSION STARTED
# UNIT TEST STARTED
@patch("controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService")
def test_update_user_perm_up_id_missing(mock_serv, client, get_valid_token):
    """Test updating user permission with missing up_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updateuserpermission",
        json={"user_id": "1", "module_id": "1", "permission_id": "1"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "mandatory" in json_data["message"].lower()


@patch("controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService")
def test_update_user_perm_up_id_not_available(mock_serv, client, get_valid_token):
    """Test updating user permission with non-existent up_id"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "message": "user id not available"}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.patch(
        "/v1/perm/updateuserpermission",
        json={"up_id": "50", "user_id": "1", "module_id": "1", "permission_id": "1"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    print(json_data)
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "not available" in json_data["message"].lower()


# Replacement for test_update_user_perm_success
def test_update_user_perm_success(client, get_valid_token, db_session):
    """Test successful update of user permission via API"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"up_id": 14, "user_id": 1, "module_id": 2, "permission_id": 1}

    # Ensure a record exists and no duplicates
    db_session.query(UserPermission).filter(
        and_(
            UserPermission.user_id == 1,
            UserPermission.module_id == 2,
            UserPermission.permission_id == 1,
        )
    ).delete()
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.add(UserPermission(id=14, user_id=1, module_id=1, permission_id=1))
    db_session.commit()

    response = client.patch(
        "/v1/perm/updateuserpermission",
        json=payload,
        headers=headers,
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True

    # Verify database update
    record = db_session.query(UserPermission).filter(UserPermission.id == 14).first()
    assert record is not None
    assert record.module_id == 2
    assert record.permission_id == 1

    # Clean up
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.commit()


# Additional test cases
def test_update_user_perm_invalid_input_format(client, get_valid_token):
    """Test updating user permission with non-integer input"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {
        "up_id": "invalid",
        "user_id": 1,
        "module_id": 1,
        "permission_id": 1,
    }

    response = client.patch(
        "/v1/perm/updateuserpermission",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 400
    json_data = response.json()
    assert "message" in json_data
    assert json_data["success"] == "false"


def test_update_user_perm_foreign_key_error(client, get_valid_token, db_session):
    """Test updating user permission with invalid foreign key"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"up_id": "14", "user_id": "999", "module_id": "1", "permission_id": "1"}

    # Ensure a record exists
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.add(UserPermission(id=14, user_id=1, module_id=1, permission_id=1))
    db_session.commit()

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService",
        return_value=(["user_id"], [999]),
    ):
        with patch(
            "controllers.v1.perm_controller.UserPerm_DBConn.updateUserPermissionDB",
            return_value=JSONResponse(
                content={"error": "Foreign key not existed."}, status_code=400
            ),
        ):
            response = client.patch(
                "/v1/perm/updateuserpermission",
                json=payload,
                headers=headers,
            )

            json_data = response.json()
            print(json_data)
            assert response.status_code == HTTP_400_BAD_REQUEST
            assert "error" in json_data
            assert "foreign key" in json_data["error"].lower()


def test_update_user_perm_database_error(client, get_valid_token, db_session):
    """Test updating user permission with general database error"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"up_id": "14", "user_id": "1", "module_id": "2", "permission_id": "1"}

    # Ensure a record exists
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.add(UserPermission(id=14, user_id=1, module_id=1, permission_id=1))
    db_session.commit()

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService",
        return_value=(["module_id"], [2]),
    ):
        with patch(
            "controllers.v1.perm_controller.UserPerm_DBConn.updateUserPermissionDB",
            return_value=JSONResponse(
                content={"error": "Database connection failed"}, status_code=400
            ),
        ):
            response = client.patch(
                "/v1/perm/updateuserpermission",
                json=payload,
                headers=headers,
            )

            assert response.status_code == HTTP_400_BAD_REQUEST
            json_data = response.json()
            assert "error" in json_data
            assert "database connection failed" in json_data["error"].lower()


def test_update_user_perm_no_changes_detected(client, get_valid_token, db_session):
    """Test updating user permission with no changes"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"up_id": "14", "user_id": "1", "module_id": "1", "permission_id": "1"}

    # Ensure a record exists
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.add(UserPermission(id=14, user_id=1, module_id=1, permission_id=1))
    db_session.commit()

    with patch(
        "controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService",
        return_value=([], []),
    ):
        response = client.patch(
            "/v1/perm/updateuserpermission",
            json=payload,
            headers=headers,
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "success" in json_data
        assert json_data["success"] == "false"
        assert "nothing to change" in json_data["message"].lower()


def test_update_user_perm_different_language(client, get_valid_token, db_session):
    """Test updating user permission with different Accept-Language header"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    payload = {"up_id": 14, "user_id": 1, "module_id": 2, "permission_id": 1}

    # Ensure a record exists and no duplicates
    db_session.query(UserPermission).filter(
        and_(
            UserPermission.user_id == 1,
            UserPermission.module_id == 2,
            UserPermission.permission_id == 1,
        )
    ).delete()
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.add(UserPermission(id=14, user_id=1, module_id=1, permission_id=1))
    db_session.commit()

    response = client.patch(
        "/v1/perm/updateuserpermission",
        json=payload,
        headers=headers,
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True

    # Clean up
    db_session.query(UserPermission).filter(UserPermission.id == 14).delete()
    db_session.commit()


def test_update_user_perm_invalid_token(client):
    """Test updating user permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    payload = {"up_id": "14", "user_id": "1", "module_id": "1", "permission_id": "1"}

    response = client.patch(
        "/v1/perm/updateuserpermission",
        json=payload,
        headers=headers,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.perm_controller.Perm_Serv.updateUserPermissionService")
def test_update_role_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    """Test add role permission with unexpected error"""
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"up_id": 14, "user_id": 1, "module_id": 1, "permission_id": 1}
    response = client.patch("/v1/perm/updateuserpermission", json=payload)
    print(response.text)
    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED
# * UPDATE USER PERMISSION ENDED

# * DELETE USER PERMISSION STARTED
# UNIT TEST STARTED


# Consolidated and fixed test_delete_user_perm_verify_id
def test_delete_user_perm_verify_id(client, get_valid_token):
    """Test deleting user permission with missing up_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleteuserpermission?up_id=")

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


# New test cases
def test_delete_user_perm_invalid_id_format(client, get_valid_token):
    """Test deleting user permission with non-integer up_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleteuserpermission?up_id=invalid")

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_delete_user_perm_non_existent_id(client, get_valid_token, db_session):
    """Test deleting user permission with non-existent up_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # Ensure no record exists
    db_session.query(UserPermission).filter(UserPermission.id == 999).delete()
    db_session.commit()

    with patch(
        "controllers.v1.perm_controller.UserPerm_DBConn.deleteUP", return_value=False
    ):
        response = client.delete("/v1/perm/deleteuserpermission?up_id=999")

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "success" in json_data
        assert json_data["success"] == "false"
        assert "not found" in json_data["message"].lower()


def test_delete_user_perm_database_error(client, get_valid_token, db_session):
    """Test deleting user permission with database error"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # Ensure a record exists
    db_session.query(UserPermission).filter_by(
        user_id=1, module_id=1, permission_id=1
    ).delete()
    # db_session.query(UserPermission).filter(UserPermission.id == 13).delete()
    data = UserPermission(user_id=1, module_id=1, permission_id=1)
    db_session.add(data)
    db_session.commit()
    db_session.refresh(data)
    up_id = data.id

    with patch(
        "controllers.v1.perm_controller.UserPerm_DBConn.deleteUP",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.delete(f"/v1/perm/deleteuserpermission?up_id={up_id}")

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data


def test_delete_user_perm_different_language(client, get_valid_token, db_session):
    """Test deleting user permission with different Accept-Language header"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}

    # Ensure a record exists
    db_session.query(UserPermission).filter_by(
        user_id=1, module_id=1, permission_id=1
    ).delete()
    # db_session.query(UserPermission).filter(UserPermission.id == 13).delete()
    data = UserPermission(user_id=1, module_id=1, permission_id=1)
    db_session.add(data)
    db_session.commit()
    db_session.refresh(data)
    up_id = data.id

    response = client.delete(f"/v1/perm/deleteuserpermission?up_id={up_id}")

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"
    assert "deleted_field" in json_data
    assert json_data["deleted_field"] == up_id

    # Verify record is marked as deleted
    record = db_session.query(UserPermission).filter(UserPermission.id == up_id).first()
    assert record is not None
    # Clean up
    db_session.query(UserPermission).filter(UserPermission.id == 13).delete()
    db_session.commit()


def test_delete_user_perm_invalid_token(client):
    """Test deleting user permission with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.delete("/v1/perm/deleteuserpermission?up_id=13")

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# Replacement for test_delete_user_perm_success
def test_delete_user_perm_success(client, get_valid_token, db_session):
    """Test successful deletion of user permission via API"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    # Ensure a record exists
    db_session.query(UserPermission).filter_by(
        user_id=1, module_id=1, permission_id=1
    ).delete()
    # db_session.query(UserPermission).filter(UserPermission.id == 13).delete()
    data = UserPermission(user_id=1, module_id=1, permission_id=1)
    db_session.add(data)
    db_session.commit()
    db_session.refresh(data)
    up_id = data.id
    response = client.delete(f"/v1/perm/deleteuserpermission?up_id={up_id}")

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "deleted successfully." in json_data["message"].lower()

    # Clean up
    db_session.query(UserPermission).filter(UserPermission.id == up_id).delete()
    db_session.commit()


@patch("controllers.v1.perm_controller.UserPerm_DBConn.deleteUP")
def test_delete_user_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleteuserpermission?up_id=13")
    assert response.status_code == HTTP_400_BAD_REQUEST


# * INTEGRATION TEST ENDED

# * DELETE USER PERMISSION ENDED
