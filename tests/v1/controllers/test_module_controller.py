from unittest.mock import patch
from urllib import response
from fastapi.responses import JSONResponse
from dao.v1.module_dao import Module_DBConn
from model.v1.module_model import Module
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
)
from tests.v1.conftest import get_or_create_by_name
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError


# * GET ALL MODULE STARTED
# UNIT TEST STARTED
def test_get_module_invalid_id_format(client, get_valid_token):
    """Test fetching a module with non-digit module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/module/getmodule?module_id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_get_all_modules(client, get_valid_token, db_session):
    """Test fetching all modules"""
    moduleData = db_session.query(Module).filter(Module.id == 1).first()
    if not moduleData:
        db_session.add(Module(name="TestModule"))
        db_session.commit()

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/module/getmodule", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "modules fetched" in json_data["message"].lower()
    assert "data" in json_data


def test_get_single_module(client, get_valid_token, db_session):
    """Test fetching a single module by module_id"""
    moduleData = db_session.query(Module).filter(Module.id == 1).first()
    if not moduleData:
        db_session.add(Module(id=1, name="TestModule"))
        db_session.commit()

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.get("/v1/module/getmodule?module_id=2", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"


# Additional test cases
@patch("controllers.v1.perm_controller.Module_DBConn.getModuleData")
def test_get_module_non_existent_id(mock_get_module, client, get_valid_token):
    """
    Test fetching a module with a non-existent module_id using mock.
    """

    # Setup mock to simulate "not found" response
    mock_get_module.return_value = []

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    response = client.get("/v1/module/getmodule?module_id=999", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    print(json_data)
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "no data found" in json_data["message"].lower()


def test_get_module_database_error(client, get_valid_token):
    """Test fetching a module with database error"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    with patch(
        "controllers.v1.perm_controller.Module_DBConn.getModuleData",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.get("/v1/module/getmodule?module_id=1", headers=headers)

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "database connection failed" in json_data["message"].lower()


def test_get_module_different_language(client, get_valid_token, db_session):
    """Test fetching a module with different Accept-Language header"""
    # Setup test data

    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.get(f"/v1/module/getmodule?module_id={id}", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


def test_get_module_invalid_token(client):
    """Test fetching a module with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.get("/v1/module/getmodule?module_id=1", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# UNIT TEST ENDED

# * GET ALL MODULE ENDED


# * ADD MODULE STARTED
# UNIT TEST STARTED


def test_add_module_missing_name(client, get_valid_token):
    """Test adding a module without providing a name"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post("/v1/module/addmodule", json={}, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert json_data["message"] == "Module name is required."


def test_add_module_already_exists(client, get_valid_token, db_session):
    """Test adding a module that already exists"""
    dummyModule = get_or_create_by_name(
        db_session, model=Module, name_value="TestModule"
    )
    module_name = "TestModule"

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.post(
        "/v1/module/addmodule", json={"name": module_name}, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "duplicate" in json_data["error"].lower()

    # Clean up
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()


# Replacement for test_add_module_success
def test_add_module_success(client, get_valid_token, db_session):
    """Test successful addition of a module via API"""
    module_name = "NewModule"
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    # Ensure no duplicate module exists
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()

    response = client.post(
        "/v1/module/addmodule", json={"name": module_name}, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert json_data["message"] == "Module Added Successfully."
    assert json_data["module name"] == module_name

    # Verify database
    module = db_session.query(Module).filter(Module.name == module_name).first()
    assert module is not None
    assert module.name == module_name

    # Clean up
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()


# Additional test cases
def test_add_module_invalid_created_by(client, get_valid_token, db_session):
    """Test adding a module with invalid createdByEmail (foreign key failure)"""
    module_name = "InvalidModule"
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    with patch(
        "controllers.v1.perm_controller.Module_DBConn.addModDB",
        return_value=JSONResponse(
            content={"success": False, "error": "Foreign key not existed."},
            status_code=400,
        ),
    ):
        response = client.post(
            "/v1/module/addmodule", json={"name": module_name}, headers=headers
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False
        assert "foreign key" in json_data["error"].lower()

    # Clean up
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()


def test_add_module_database_error(client, get_valid_token, db_session):
    """Test adding a module with general database error"""
    module_name = "ErrorModule"
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}

    with patch(
        "controllers.v1.perm_controller.Module_DBConn.addModDB",
        return_value=JSONResponse(
            content={"success": False, "error": "Database connection failed"},
            status_code=400,
        ),
    ):
        response = client.post(
            "/v1/module/addmodule", json={"name": module_name}, headers=headers
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False
        assert "database connection failed" in json_data["error"].lower()

    # Clean up
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()


def test_add_module_different_language(client, get_valid_token, db_session):
    """Test adding a module with different Accept-Language header"""
    module_name = "LangModule"
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}

    # Ensure no duplicate module exists
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()

    response = client.post(
        "/v1/module/addmodule", json={"name": module_name}, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == True
    assert "module name" in json_data
    assert json_data["module name"] == module_name

    # Verify database
    module = db_session.query(Module).filter(Module.name == module_name).first()
    assert module is not None
    assert module.name == module_name

    # Clean up
    db_session.query(Module).filter(Module.name == module_name).delete()
    db_session.commit()


def test_add_module_duplicate_error():
    db = MagicMock()
    db.add.side_effect = IntegrityError(
        statement=None, params=None, orig=Exception("1062 Duplicate entry")
    )

    response = Module_DBConn.addModDB("TestModule", 1, db)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body is not None
    assert b"Duplicate entry" in response.body


def test_add_module_integrity_error_generic():
    db = MagicMock()
    db.add.side_effect = IntegrityError(
        statement=None,
        params=None,
        orig=Exception("1452 Cannot add or update a child row"),
    )

    response = Module_DBConn.addModDB("TestModule", "admin", db)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert b"Database integrity error" in response.body


def test_add_module_general_exception():
    db = MagicMock()
    db.add.side_effect = Exception("Something unexpected")

    response = Module_DBConn.addModDB("TestModule", "admin", db)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert b"Something unexpected" in response.body


def test_add_module_invalid_token(client):
    """Test adding a module with missing or invalid token"""
    module_name = "NoAuthModule"
    headers = {"Accept-Language": "en"}

    response = client.post(
        "/v1/module/addmodule", json={"name": module_name}, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.perm_controller.Module_DBConn.addModDB")
def test_add_module_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"name": "NoAuthModule"}
    response = client.post("/v1/module/addmodule", json=payload, headers=headers)
    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED

# * ADD MODULE ENDED

# * UPDATE MODULE ENDED


# UNIT TEST STARTED
# Fixed test cases
def test_update_module_missing_module_id(client, get_valid_token):
    """Test updating a module without module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule", json={"name": "UpdatedModule"}, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "mandatory" in json_data["message"].lower()


def test_update_module_non_existent_id(client, get_valid_token, db_session):
    """Test updating a module with non-existent module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": "999", "name": "NewModule"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "not available" in json_data["message"].lower()


@patch("controllers.v1.perm_controller.Module_DBConn.updateModuleDB")
def test_update_module_duplicate_name(mock_update, client, get_valid_token, db_session):
    """Test updating a module to a duplicate name"""
    # Setup test data
    dummy_module = Module(name="TestModule")
    db_session.add(dummy_module)
    db_session.commit()
    db_session.refresh(dummy_module)

    id = dummy_module.id

    mock_update.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": id, "name": "TestModule"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "duplicate module" in json_data["message"].lower()

    # Clean up
    db_session.query(Module).filter(Module.name == "TestModule").delete()
    db_session.commit()


# Replacement for test_update_module_success
def test_update_module_success(client, get_valid_token, db_session):
    """Test successful update of a module via API"""
    # Setup test data

    dummy_module = Module(name="TestModule")
    db_session.add(dummy_module)
    db_session.commit()
    db_session.refresh(dummy_module)

    id = dummy_module.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": id, "name": "UpdatedModule"},
        headers=headers,
    )
    print(response.text)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "updated successfully" in json_data["message"].lower()

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


# Additional test cases
def test_update_module_invalid_id_format(client, get_valid_token):
    """Test updating a module with non-integer module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": "invalid", "name": "NewModule"},
        headers=headers,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == False
    assert "invalid" in json_data["message"].lower()


def test_update_module_duplicate_error():
    db = MagicMock()

    # Mock update to raise IntegrityError with "1062" code
    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.update.side_effect = IntegrityError(
        statement=None, params=None, orig=Exception("1062 Duplicate entry")
    )

    response = Module_DBConn.updateModuleDB(
        recentUpdate=["name"],
        data2update=["duplicate_module"],
        module_id=1,
        db=db,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Duplicate entry"}'


def test_update_module_integrity_error():
    db = MagicMock()

    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.update.side_effect = IntegrityError(
        statement=None, params=None, orig=Exception("Some other integrity issue")
    )

    response = Module_DBConn.updateModuleDB(
        recentUpdate=["name"],
        data2update=["invalid_module"],
        module_id=1,
        db=db,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Database integrity error"}'


def test_update_module_general_exception():
    db = MagicMock()

    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.update.side_effect = Exception("Something went wrong")

    response = Module_DBConn.updateModuleDB(
        recentUpdate=["name"],
        data2update=["something_weird"],
        module_id=1,
        db=db,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert response.body == b'{"success":false,"error":"Something went wrong"}'


def test_update_module_database_error(client, get_valid_token, db_session):
    """Test updating a module with general database error"""
    # Setup test data

    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id

    with patch(
        "controllers.v1.perm_controller.Module_DBConn.updateModuleDB",
        return_value=JSONResponse(
            content={"success": False, "error": "Database connection failed"},
            status_code=400,
        ),
    ):
        headers = {
            "Authorization": f"Bearer {get_valid_token}",
            "Accept-Language": "en",
        }
        response = client.patch(
            "/v1/module/updatemodule",
            json={"module_id": id, "name": "OldModule"},
            headers=headers,
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "error" in json_data
        assert "success" in json_data
        assert json_data["success"] == False
        assert "database connection failed" in json_data["error"].lower()

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


def test_update_module_different_language(client, get_valid_token, db_session):
    """Test updating a module with different Accept-Language header"""
    # Setup test data
    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": id, "name": "UpdatedModule"},
        headers=headers,
    )
    print(response.text)
    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


def test_update_module_invalid_token(client):
    """Test updating a module with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.patch(
        "/v1/module/updatemodule",
        json={"module_id": "1", "name": "NewModule"},
        headers=headers,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.perm_controller.Module_Serv.updateModule_Serv")
def test_update_module_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    """Test update module with unexpected error"""
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    payload = {"module_id": 1, "name": "UpdatedModule"}
    response = client.patch("/v1/module/updatemodule", json=payload, headers=headers)
    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED
# * UPDATE MODULE ENDED


# * DELETE MODULE STARTED
# UNIT TEST STARTED


# Fixed test cases


def test_delete_module_exception():
    db = MagicMock()

    # Simulate update raising an exception
    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.update.side_effect = Exception("Unexpected DB error")

    result = Module_DBConn.deleteModuleDB(module_id=1, db=db)

    assert result is False
    db.rollback.assert_called_once()


def test_delete_module_missing_id(client, get_valid_token):
    """Test deleting a module without module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/module/deletemodule?module_id=", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_module_invalid_id_format(client, get_valid_token):
    """Test deleting a module with non-digit module_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/module/deletemodule?module_id=abc", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_module_non_existent_id(client, get_valid_token, db_session):
    """Test deleting a module with non-existent module_id"""
    # Ensure no module with id=150 exists
    db_session.query(Module).filter(Module.id == 150).delete()
    db_session.commit()

    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/module/deletemodule?module_id=150", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "false"
    assert "not found" in json_data["message"].lower()


# Replacement for test_delete_module_success
def test_delete_module_success(client, get_valid_token, db_session):
    """Test successful deletion of a module via API"""
    # Setup test data
    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id
    print("id", id)
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete(f"/v1/module/deletemodule?module_id={id}", headers=headers)
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "message" in json_data
    assert "success" in json_data
    assert json_data["success"] == "true"
    assert "deleted successfully" in json_data["message"].lower()

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


# Additional test cases
def test_delete_module_database_error(client, get_valid_token, db_session):
    """Test deleting a module with database error"""
    # Setup test data
    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id
    with patch(
        "controllers.v1.perm_controller.Module_DBConn.deleteModuleDB",
        return_value=False,
    ):
        headers = {
            "Authorization": f"Bearer {get_valid_token}",
            "Accept-Language": "en",
        }
        response = client.delete(
            f"/v1/module/deletemodule?module_id={id}", headers=headers
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "message" in json_data
        assert "success" in json_data
        assert json_data["success"] == "false"

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


def test_delete_module_different_language(client, get_valid_token, db_session):
    """Test deleting a module with different Accept-Language header"""
    # Setup test data
    dummyModule = get_or_create_by_name(db_session, Module, name_value="OldModule")
    id = dummyModule.id
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "es"}
    response = client.delete(f"/v1/module/deletemodule?module_id={id}", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert "Mensaje" in json_data
    assert "success" in json_data
    assert json_data["success"] == "Verdadero"
    assert "deleted_field" in json_data

    # Clean up
    db_session.query(Module).filter(Module.id == id).delete()
    db_session.commit()


def test_delete_module_invalid_token(client):
    """Test deleting a module with missing or invalid token"""
    headers = {"Accept-Language": "en"}
    response = client.delete("/v1/module/deletemodule?module_id=10", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch("controllers.v1.perm_controller.Module_Serv.deleteModule_Serv")
def test_delete_module_unexpected_error(
    mock_verify_module_role_perm_id, client, get_valid_token
):
    mock_verify_module_role_perm_id.side_effect = Exception("unexpected error")
    headers = {"Authorization": f"Bearer {get_valid_token}", "Accept-Language": "en"}
    response = client.delete("/v1/module/deletemodule?module_id=10", headers=headers)
    assert response.status_code == HTTP_400_BAD_REQUEST


# INTEGRATION TEST ENDED

# * DELETE MODULE ENDED
