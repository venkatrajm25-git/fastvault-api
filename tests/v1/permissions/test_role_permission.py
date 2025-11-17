from sqlalchemy.exc import IntegrityError
import json
from unittest.mock import patch, AsyncMock, MagicMock

# from helpers.v1.helpers import fetchRecord
from dao.v1.perm_dao import RolePerm_DBConn
from fastapi.responses import JSONResponse
from model.v1.permission_model import RolePermission
from sqlalchemy import and_, null
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from tests.v1.conftest import db_session

# * GET ALL ROLE PERMISSION STARTED
# UNIT TEST STARTED


class MockRolePermDBConn:
    @staticmethod
    def getRPData(db):
        return [
            type("obj", (), {"role_id": 1, "module_id": 101, "permission_id": 1001}),
            type("obj", (), {"role_id": 1, "module_id": 102, "permission_id": 1002}),
            type("obj", (), {"role_id": 2, "module_id": 103, "permission_id": 1003}),
        ]


def test_getRolePermission_all(client, get_valid_token):
    """Test fetching all role permissions with valid token and language header"""
    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.getRPData",
        MockRolePermDBConn.getRPData,
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")

        response = client.get("/v1/perm/getrolepermission")

        assert response.status_code == HTTP_200_OK
        json_data = response.json()

        assert "message" in json_data
        assert json_data["message"] == "Fetched all roles successfully."


def test_get_role_permission_not_found(client, get_valid_token):
    """Test fetching permissions for non-existent role ID"""
    # with patch(
    #     "controllers.v1.perm_controller.RolePerm_DBConn.getRPData",
    #     MockRolePermDBConn.getRPData,
    # ) as mock_getRPData:
    # Patch the DB call to return mock data with only role_ids 1 and 2
    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.getRPData"
    ) as mock_getRPData:

        # This mock ensures role_id 999 is not found in the data
        mock_getRPData.return_value = [
            type("obj", (), {"role_id": 1, "module_id": 101, "permission_id": 1001}),
            type("obj", (), {"role_id": 1, "module_id": 102, "permission_id": 1002}),
            type("obj", (), {"role_id": 2, "module_id": 103, "permission_id": 1003}),
        ]

        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        invalid_role_id = 999

        response = client.get(f"/v1/perm/getrolepermission?role_id={invalid_role_id}")

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Role ID Not Found."


def test_getRolePermission_with_valid_role_id(client, get_valid_token):
    """Test fetching permissions for a valid role ID"""
    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.getRPData",
        MockRolePermDBConn.getRPData,
    ) as mock_getRPData:
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")

        response = client.get("/v1/perm/getrolepermission?role_id=1")

        assert response.status_code == HTTP_200_OK
        json_data = response.json()

        assert "message" in json_data
        assert json_data["message"] == "Role permission fetched."


def test_get_specific_role_permissions(client, get_valid_token):
    """Test fetching specific role permissions with different language"""
    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.getRPData",
        MockRolePermDBConn.getRPData,
    ):
        role_id = 2
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")

        response = client.get(f"/v1/perm/getrolepermission?role_id={role_id}")

        assert response.status_code == HTTP_200_OK
        json_data = response.json()

        assert "message" in json_data


def test_get_all_roles_success(client, get_valid_token):
    """Test fetching all roles with mocked empty database"""
    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.getRPData", lambda db: []
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")

        response = client.get("/v1/perm/getrolepermission")

        assert response.status_code == HTTP_200_OK
        json_data = response.json()

        assert "message" in json_data
        assert json_data["message"] == "Fetched all roles successfully."


def test_getRolePermission_invalid_role_id_format(client, get_valid_token):
    """Test with invalid role_id format (non-integer)"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.get("/v1/perm/getrolepermission?role_id=invalid")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


# UNIT TEST END
# * GET ALL ROLE PERMISSION ENDED


# * ADD ROLE PERMISSION STARTED
# UNIT TEST STARTED
def mock_verify_module_role_perm_id(
    role_id, module_id, permission_id, db, accept_language
):
    valid_roles = {1, 2, 3}  # Include role_id 3 for integration test
    valid_modules = {1, 2}
    valid_permissions = {1, 2}

    if role_id not in valid_roles:
        return JSONResponse(
            content={"message": "Role id not available."}, status_code=400
        )
    if module_id not in valid_modules:
        return JSONResponse(
            content={"message": "Module id not available."}, status_code=400
        )
    if permission_id not in valid_permissions:
        return JSONResponse(
            content={"message": "Permission id not available."}, status_code=400
        )
    return JSONResponse(content={"message": "Valid IDs"}, status_code=200)


def test_add_role_perm_missing_fields(client, get_valid_token):
    """Test with missing or empty role_id, module_id, or permission_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    test_cases = [
        {"role_id": "", "module_id": 1, "permission_id": 1},
        {"role_id": 1, "module_id": "", "permission_id": 1},
        {"role_id": 1, "module_id": 1, "permission_id": ""},
        {"module_id": 1, "permission_id": 1},
        {"role_id": 1, "permission_id": 1},
        {"role_id": 1, "module_id": 1},
    ]

    for payload in test_cases:
        response = client.post(
            "/v1/perm/addrolepermission",
            json=payload,
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "success" in json_data
        assert json_data["success"] == False


def test_add_role_perm_role_id_not_available(client, get_valid_token):
    """Test with invalid role_id"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        payload = {"role_id": 150, "module_id": 1, "permission_id": 1}

        response = client.post(
            "/v1/perm/addrolepermission",
            json=payload,
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Role id not available."


def test_add_role_perm_module_id_not_available(client, get_valid_token):
    """Test with invalid module_id"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        payload = {"role_id": 1, "module_id": 1, "permission_id": 1}

        response = client.post(
            "/v1/perm/addrolepermission",
            json=payload,
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Module id not available."


def test_add_role_perm_permission_id_not_available(client, get_valid_token):
    """Test with invalid permission_id"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        payload = {"role_id": 1, "module_id": 1, "permission_id": 150}

        response = client.post(
            "/v1/perm/addrolepermission",
            json=payload,
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Permission id not available."


def test_add_role_perm_success(client, get_valid_token):
    """Test successful addition of role permission"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(
            return_value=JSONResponse(content={"message": "Valid IDs"}, status_code=200)
        ),
    ):
        with patch(
            "controllers.v1.perm_controller.RolePerm_DBConn.addRolePerm",
            return_value=True,
        ):
            client.cookies.clear()

            # Attach valid JWT to cookies
            client.cookies.set("access_token", get_valid_token, path="/")
            payload = {"role_id": 1, "module_id": 1, "permission_id": 1}

            response = client.post(
                "/v1/perm/addrolepermission",
                json=payload,
            )
            assert response.status_code == HTTP_201_CREATED
            json_data = response.json()
            assert "message" in json_data
            assert "success" in json_data
            assert json_data["success"] == "true"
            assert "added successfully" in json_data["message"].lower()


def test_add_role_perm_invalid_token(client):
    """Test with missing authorization token"""
    payload = {"role_id": 1, "module_id": 1, "permission_id": 1}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "message" in json_data


def test_add_role_perm_role_id_not_available(client, get_valid_token):
    """Test with invalid role_id"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    ):
        client.cookies.clear()

        # Attach valid JWT to cookies
        client.cookies.set("access_token", get_valid_token, path="/")
        payload = {"role_id": 99999, "module_id": 1, "permission_id": 1}

        response = client.post(
            "/v1/perm/addrolepermission",
            json=payload,
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Role id not available."


def test_add_role_perm_module_id_not_available(client, get_valid_token):
    """Test with invalid module_id"""
    # with patch(
    #     "controllers.v1.perm_controller.verifyModuleRolendPermID",
    #     new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    # ):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 1, "module_id": 99999, "permission_id": 1}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert json_data["message"] == "Module ID is not available."


def test_add_role_perm_permission_id_not_available(client, get_valid_token):
    """Test with invalid permission_id"""
    # with patch(
    #     "controllers.v1.perm_controller.verifyModuleRolendPermID",
    #      new=AsyncMock(side_effect=mock_verify_module_role_perm_id),
    # ):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 1, "module_id": 1, "permission_id": 15000}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert json_data["message"] == "Permission ID is not available."


def test_add_role_perm_success(client, get_valid_token):
    """Test successful addition of role permission"""
    with patch(
        "controllers.v1.perm_controller.verifyModuleRolendPermID",
        new=AsyncMock(
            return_value=JSONResponse(content={"message": "Valid IDs"}, status_code=200)
        ),
    ):
        with patch(
            "controllers.v1.perm_controller.RolePerm_DBConn.addRolePerm",
            return_value=JSONResponse(
                content={
                    "message": "Role Permission added successfully.",
                    "success": "true",
                },
                status_code=201,
            ),
        ):
            headers = {
                "Authorization": f"Bearer {get_valid_token}",
                "Accept-Language": "en",
            }
            payload = {"role_id": 1, "module_id": 1, "permission_id": 1}

            response = client.post(
                "/v1/perm/addrolepermission",
                json=payload,
            )
            json_data = response.json()
            print("JSON DATA: *", json_data)
            assert response.status_code == HTTP_201_CREATED
            assert "message" in json_data
            assert "success" in json_data
            assert json_data["success"] == "true"
            assert "added successfully" in json_data["message"].lower()


def test_add_role_perm_invalid_token(client):
    """Test with missing authorization token"""
    headers = {"Accept-Language": "en"}
    payload = {"role_id": 1, "module_id": 1, "permission_id": 1}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


def test_add_role_perm_invalid_input_format(client, get_valid_token):
    """Test with non-integer input for IDs"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "invalid", "module_id": 1, "permission_id": 1}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert (
        "value_error" in json_data["message"].lower()
        or "invalid" in json_data["message"].lower()
    )


def test_add_role_perm_success_integration(client, get_valid_token, db_session):
    """Integration test for successful role permission addition"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 3, "module_id": 1, "permission_id": 1}
    db_session.query(RolePermission).filter_by(
        role_id=3, module_id=1, permission_id=1
    ).delete()
    db_session.commit()

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "added successfully" in json_data["message"].lower()

    # Clean up
    db_session.query(RolePermission).filter(
        and_(
            RolePermission.role_id == 3,
            RolePermission.module_id == 1,
            RolePermission.permission_id == 1,
        )
    ).delete()
    db_session.commit()


def test_add_role_perm_duplicate_integration(client, get_valid_token, db_session):
    """Integration test for duplicate role permission"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 3, "module_id": 1, "permission_id": 1}

    # Ensure the record doesn't exist before the test
    db_session.query(RolePermission).filter(
        and_(
            RolePermission.role_id == 3,
            RolePermission.module_id == 1,
            RolePermission.permission_id == 1,
        )
    ).delete()
    db_session.commit()

    # Add first record
    first_response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert first_response.status_code == HTTP_201_CREATED
    first_response_json = first_response.json()
    assert "message" in first_response_json
    assert "success" in first_response_json
    assert first_response_json["success"] == True
    assert "added successfully." in first_response_json["message"].lower()

    # Verify record exists in the database
    record = (
        db_session.query(RolePermission)
        .filter(
            and_(
                RolePermission.role_id == 3,
                RolePermission.module_id == 1,
                RolePermission.permission_id == 1,
            )
        )
        .first()
    )
    assert record is not None, "First record was not added to the database"

    # Try adding the same record again
    second_response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert (
        second_response.status_code == HTTP_400_BAD_REQUEST
    ), f"Expected 400, got {second_response.status_code}: {second_response.json()}"
    second_response_json = second_response.json()
    assert "error" in second_response_json
    assert "success" in second_response_json
    assert second_response_json["success"] == False

    # Clean up
    db_session.query(RolePermission).filter(
        and_(
            RolePermission.role_id == 3,
            RolePermission.module_id == 1,
            RolePermission.permission_id == 1,
        )
    ).delete()
    db_session.commit()

    # def test_add_role_permission_foreign_key_contraint(client, get_valid_token, db_session):
    #     rpData = db_session.query(RolePermission).first()
    #     if not rpData:
    #         NewRP = RolePermission(role_id=1, module_id=1, permission_id=1)
    #         db_session.add(NewRP)
    #         db_session.commit()
    #         db_session.refresh(NewRP)
    #         rpData = NewRP
    #     print("hi")
    #     client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")


#     payload = {
#         "role_id": rpData.role_id,
#         "module_id": 9999,
#         "permission_id": rpData.permission_id,
#     }

#     response = client.post(
#         "/v1/perm/addrolepermission",
#         json=payload,
#
#     )
#     print("response===", response.text)
#     assert response.status_code == HTTP_200_OK


def test_add_role_perm_invalid_input_format(client, get_valid_token):
    """Test with non-integer input for IDs"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": "invalid", "module_id": 1, "permission_id": 1}

    response = client.post(
        "/v1/perm/addrolepermission",
        json=payload,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data


@patch("controllers.v1.perm_controller.RolePerm_DBConn.addRolePerm")
def test_add_role_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    """Test add role permission with unexpected error"""
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 1, "module_id": 1, "permission_id": 1}
    response = client.post("/v1/perm/addrolepermission", json=payload)
    assert response.status_code == HTTP_400_BAD_REQUEST


# * UPDATE ROLE PERMISSION STARTED
# UNIT TEST STARTED
def test_update_role_perm_invalid_input_format(client, get_valid_token):
    """Test updating role permission with non-integer input"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {
        "rp_id": "invalid",
        "role_id": 1,
        "module_id": 1,
        "permission_id": 1,
    }

    response = client.patch(
        "/v1/perm/updaterolepermission",
        json=payload,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data


def test_update_role_perm_missing_optional_fields(client, get_valid_token, db_session):
    """Test updating role permission with missing optional fields"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rp_id": 14}

    # Ensure no conflicting records exist
    db_session.query(RolePermission).filter(
        and_(
            RolePermission.role_id == 1,
            RolePermission.module_id == 1,
            RolePermission.permission_id == 1,
        )
    ).delete()
    db_session.query(RolePermission).filter(RolePermission.id == 14).delete()
    db_session.commit()
    db_session.flush()
    db_session.add(RolePermission(id=14, role_id=1, module_id=1, permission_id=1))
    db_session.commit()

    response = client.patch(
        "/v1/perm/updaterolepermission",
        json=payload,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data

    # Clean up
    db_session.query(RolePermission).filter(RolePermission.id == 14).delete()
    db_session.commit()


def test_update_role_perm_missing_rp_id(client, get_valid_token):
    """Test update role permission when rp_id is missing"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    payload = {
        # "rp_id": "14",  # Intentionally missing
        "role_id": 1,
        "module_id": 1,
        "permission_id": 1,
    }

    response = client.patch(
        "/v1/perm/updaterolepermission",
        json=payload,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "mandatory" in json_data["message"].lower()


def test_update_role_perm_not_available(client, get_valid_token):
    """Force test to simulate database error response"""
    # with patch(
    #     "routes.v1.perm_route.update_role_permission",
    #     side_effect=Exception("Foreign key not existed."),
    # ):
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {
        "rp_id": 14,
        "role_id": 1,
        "module_id": 50,
        "permission_id": 1,
    }

    response = client.patch(
        "/v1/perm/updaterolepermission",
        json=payload,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data


@patch("controllers.v1.perm_controller.PermissionModule.updateRolePermission")
def test_update_role_perm_no_changes_detected(mock_serv, client, get_valid_token):
    """Test updating role permission with no changes"""
    mock_serv.return_value = JSONResponse(
        content={"message": "No changes detected"}, status_code=400
    )

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rp_id": 14, "role_id": 1, "module_id": 1, "permission_id": 1}

    response = client.patch(
        "/v1/perm/updaterolepermission",
        json=payload,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "no changes detected" in json_data["message"].lower()


@patch("controllers.v1.perm_controller.Perm_Serv.updateRolePermissionService")
def test_update_role_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    """Test add role permission with unexpected error"""
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"role_id": 1, "module_id": 1, "permission_id": 1}
    response = client.patch("/v1/perm/updaterolepermission", json=payload)
    assert response.status_code == HTTP_400_BAD_REQUEST


# * UPDATE ROLE PERMISSION ENDED

# * DELETE ROLE PERMISSION STARTED
# UNIT TEST STARTED


@patch("controllers.v1.perm_controller.RolePerm_DBConn.deleteRp")
def test_delete_role_perm_verify_id(mock_delete, client, get_valid_token):
    """Test deleting role permission with missing rp_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleterolepermission?rp_id=")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.perm_controller.RolePerm_DBConn.getRPData")
def test_delete_role_perm_not_found(mock_get_rpdata, client, get_valid_token):
    """
    When the requested rp_id is absent in DB, the controller
    must return 400 with “Role Permission Not found”.
    """
    mock_get_rpdata.return_value = [
        type("obj", (), {"id": 1}),
        type("obj", (), {"id": 2}),
    ]

    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")

    response = client.delete("/v1/perm/deleterolepermission?rp_id=99")

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "Role Permission Not found"
    assert json_data["success"] is False


# New test cases
def test_delete_role_perm_invalid_id_format(client, get_valid_token):
    """Test deleting role permission with non-integer rp_id"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleterolepermission?rp_id=invalid")

    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    json_data = response.json()
    assert "detail" in json_data


def test_delete_role_perm_database_error(client, get_valid_token, db_session):
    """Test deleting role permission with database error"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rp_id": 33}

    # Ensure a record exists
    db_session.query(RolePermission).filter(RolePermission.id == 33).delete()
    db_session.add(RolePermission(id=33, role_id=1, module_id=1, permission_id=1))
    db_session.commit()

    with patch(
        "controllers.v1.perm_controller.RolePerm_DBConn.deleteRp",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.delete("/v1/perm/deleterolepermission?rp_id=33")
        print(response.text)
        assert response.status_code == HTTP_400_BAD_REQUEST


def test_delete_role_perm_invalid_token(client):
    """Test deleting role permission with missing or invalid token"""
    response = client.delete("/v1/perm/deleterolepermission?rp_id=33")

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# Replacement for test_delete_role_perm_success
def test_delete_role_perm_success(client, get_valid_token, db_session):
    """Test successful deletion of role permission via API"""
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    payload = {"rp_id": 33}

    # Ensure a record exists
    db_session.query(RolePermission).filter(RolePermission.id == 33).delete()
    db_session.commit()

    rp = RolePermission(id=33, role_id=1, module_id=1, permission_id=1)
    db_session.add(rp)
    db_session.commit()

    assert db_session.query(RolePermission).filter_by(id=33).first() is not None

    response = client.delete("/v1/perm/deleterolepermission?rp_id=33")
    print("reason", response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True


@patch("controllers.v1.perm_controller.RolePerm_DBConn.deleteRp")
def test_delete_role_permission_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    client.cookies.clear()

    # Attach valid JWT to cookies
    client.cookies.set("access_token", get_valid_token, path="/")
    response = client.delete("/v1/perm/deleterolepermission?rp_id=33")
    assert response.status_code == HTTP_400_BAD_REQUEST


# * INTEGRATION TEST ENDED

# * DELETE ROLE PERMISSION ENDED
