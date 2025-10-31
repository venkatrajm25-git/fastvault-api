import json
from unittest.mock import MagicMock, patch
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from dao.v1.risk_type_dao import RiskTypeDAO

# GET RISK TYPE STARTED


@patch("controllers.v1.risk_type_controller.RiskTypeServices.get_risk_type_serv")
def test_get_risk_type_with_data(mock_serv, client, get_valid_token):
    """Test successful retrieval of risk types with data"""
    mock_serv.return_value = {
        "success": True,
        "message": "Data fetched successfully",
        "data": {
            "list": [
                {"id": 1, "name": "Regulatory", "status": 1},
                {"id": 2, "name": "Technology", "status": 0},
            ]
        },
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/risk-type/get_risktype", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"
    assert len(json_data["data"]["list"]) == 2
    assert json_data["data"]["list"][0]["name"] == "Regulatory"
    assert json_data["data"]["list"][1]["name"] == "Technology"


@patch("controllers.v1.risk_type_controller.RiskTypeServices.get_risk_type_serv")
def test_get_risk_type_empty(mock_serv, client, get_valid_token):
    """Test retrieval of risk types with no data"""
    mock_serv.return_value = {
        "success": True,
        "message": "No risk-types found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/risk-type/get_risktype", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No risk-types found"
    assert json_data["data"]["list"] == []


@patch("controllers.v1.risk_type_controller.RiskTypeServices.get_risk_type_serv")
def test_get_risk_type_database_error(mock_serv, client, get_valid_token):
    """Test retrieval of risk types with database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/risk-type/get_risktype", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_risk_type_invalid_token(client):
    """Test retrieval of risk types with missing or invalid token"""
    headers = {}
    response = client.get("v1/risk-type/get_risktype", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET RISK TYPE ENDED


# ADD RISK TYPE STARTED


@patch("controllers.v1.risk_type_controller.RiskTypeServices.add_risk_type_serv")
def test_add_risk_type_success(mock_serv, client, get_valid_token):
    """Test successful addition of risk type"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Data Added Successfully",
            "Risk Type ID": 101,
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Regulatory", "status": 1}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data Added Successfully"
    assert json_data["Risk Type ID"] == 101


@patch("controllers.v1.risk_type_controller.RiskTypeServices.add_risk_type_serv")
def test_add_risk_type_duplicate(mock_serv, client, get_valid_token):
    """Test adding risk type with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Duplicate Risk", "status": 1, "modified_by": None}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch("controllers.v1.risk_type_controller.RiskTypeServices.add_risk_type_serv")
def test_add_risk_type_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding risk type with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Invalid Risk", "status": 1, "modified_by": 999}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


# @patch("controllers.v1.risk_type_controller.RiskTypeServices.add_risk_type_serv")
# def test_add_risk_type_database_integrity_error(mock_serv, client, get_valid_token):
#     """Test adding risk type with Database integrity error"""
#     mock_serv.return_value = JSONResponse(
#         content={"success": False, "error": "Database integrity error"}, status_code=400
#     )
#     headers = {"Authorization": f"Bearer {get_valid_token}"}
#     payload = {"risk_type": "Invalid Risk", "status": 1, "modified_by": 1}
#     response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

#     assert response.status_code == HTTP_400_BAD_REQUEST
#     json_data = response.json()
#     assert json_data["success"] is False
#     assert json_data["error"] == "Database integrity error"


@patch("services.v1.risk_type_services.RiskTypeDAO.addRiskType")
def test_add_risk_type_exception(mock_serv, client, get_valid_token):
    """Test adding risk type with Database integrity error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Unexpected error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Invalid Risk", "status": 1, "modified_by": 1}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Unexpected error"


# def test_add_risk_type_generic_error(client, get_valid_token):
#     """Test adding risk type with general database error"""
#     headers = {"Authorization": f"Bearer {get_valid_token}"}
#     payload = {"risk_type": "System Failure", "status": 1, "modified_by": None}
#     with patch(
#         "services.v1.risk_type_services.RiskTypeDAO.addRiskType",
#         side_effect=Exception("Database integrity error"),
#     ):
#         response = client.post(
#             "/v1/risk-type/add_risktype", json=payload, headers=headers
#         )
#         print(response.text)
#         assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
#         json_data = response.json()
#         assert json_data["success"] is False
#         assert "Database integrity error" in json_data["error"]


# def test_add_risk_type_integrity_error(db_session):
#     # Now call the DAO directly
#     with patch(
#         "services.v1.risk_type_services.RiskTypeDAO.addRiskType",
#         side_effect=Exception("Database integrity error"),
#     ):
#         response = RiskTypeDAO.addRiskType(dataList=["testing", 1, 1], db=db_session)

#         assert isinstance(response, JSONResponse)
#         assert response.status_code == 400
#         assert b"Database integrity error" in response.body


def test_add_risk_type_duplicate(client, get_valid_token):
    """Test adding risk type with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Regulatory"}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "duplicate" in str(json_data["error"]).lower()


@patch("controllers.v1.risk_type_controller.RiskTypeServices.add_risk_type_serv")
def test_add_risk_type_unexpected_error(mock_serv, client, get_valid_token):
    """Test add_risk_type with unexpected error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_type": "Regulatory", "status": 1}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert "error" in json_data


def test_add_risk_type_invalid_token(client):
    """Test adding risk type with missing or invalid token"""
    headers = {}
    payload = {"risk_type": "Regulatory", "status": 1, "modified_by": None}
    response = client.post("/v1/risk-type/add_risktype", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# ADD RISK TYPE ENDED

# GET RISK GOVERNANCE - RISK TYPE STARTED


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_risk_governance_risktype_serv"
)
def test_get_risk_governance_risktype_success(mock_serv, client, get_valid_token):
    """Test successful retrieval of risk governance types with data"""
    mock_serv.return_value = {
        "success": True,
        "message": "Data fetched successfully",
        "data": {
            "list": [
                {"id": 1, "risk_governance_id": 101, "risk_type_id": 201, "status": 1},
                {"id": 2, "risk_governance_id": 102, "risk_type_id": 202, "status": 1},
            ]
        },
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_risk_governance_risk_type", headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"
    assert len(json_data["data"]["list"]) == 2
    assert json_data["data"]["list"][0]["risk_governance_id"] == 101
    assert json_data["data"]["list"][1]["risk_governance_id"] == 102


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_risk_governance_risktype_serv"
)
def test_get_risk_governance_risktype_empty(mock_serv, client, get_valid_token):
    """Test retrieval of risk governance types with no data"""
    mock_serv.return_value = {
        "success": True,
        "message": "No Risk Governance - Risk Types found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_risk_governance_risk_type", headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No Risk Governance - Risk Types found"
    assert json_data["data"]["list"] == []


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_risk_governance_risktype_serv"
)
def test_get_risk_governance_risktype_database_error(
    mock_serv, client, get_valid_token
):
    """Test retrieval of risk governance types with database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_risk_governance_risk_type", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_risk_governance_risktype_invalid_token(client):
    """Test retrieval of risk governance types with missing or invalid token"""
    headers = {}
    response = client.get(
        "/v1/risk-type/get_risk_governance_risk_type", headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET RISK GOVERNANCE - RISK TYPE ENDED


# ADD RISK GOVERNANCE - RISK TYPE STARTED


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_risk_governance_risk_type_serv"
)
def test_add_risk_governance_risk_type_success(mock_serv, client, get_valid_token):
    """Test successful addition of risk governance risk type"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Risk Governance - Risk Type added successfully.",
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 1, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Risk Governance added successfully"


@patch("services.v1.risk_type_services.RiskTypeDAO.addRiskGoverance_RiskType")
def test_add_risk_governance_risk_type_duplicate(mock_serv, client, get_valid_token):
    """Test adding risk governance risk type with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 1, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    print("response", response.text)
    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Risk Governance not added"


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_risk_governance_risk_type_serv"
)
def test_add_risk_governance_risk_type_foreign_key_error(
    mock_serv, client, get_valid_token
):
    """Test adding risk governance risk type with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 999, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Risk Governance not added"


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_risk_governance_risk_type_serv"
)
def test_add_risk_governance_risk_type_generic_error(
    mock_serv, client, get_valid_token
):
    """Test adding risk governance risk type with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 1, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Risk Governance not added"


def test_add_risk_governance_risk_type_invalid_payload(client, get_valid_token):
    """Test adding risk governance risk type with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 1, "status": 1}  # Missing risk_type_id
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_add_risk_governance_risk_type_invalid_token(client):
    """Test adding risk governance risk type with missing or invalid token"""
    headers = {}
    payload = {"risk_governance_id": 1, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_risk_governance_risk_type_serv"
)
def test_add_risk_governance_risk_type_unexpected_error(
    mock_serv, client, get_valid_token
):
    """Test add_risk_governance_risk_type with unexpected error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_governance_id": 1, "risk_type_id": 2, "status": 1}
    response = client.post(
        "/v1/risk-type/add_risk_governance_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


# ADD RISK GOVERNANCE - RISK TYPE ENDED

# GET BUSINESS RISK TYPES STARTED


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_success(mock_serv, client, get_valid_token):
    """Test successful retrieval of business risk types with data"""
    mock_serv.return_value = {
        "success": True,
        "message": "Data fetched successfully",
        "data": {
            "list": [
                {"id": 1, "name": "Cyber Risk"},
                {"id": 2, "name": "Compliance Risk"},
            ]
        },
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"
    assert len(json_data["data"]["list"]) == 2
    assert json_data["data"]["list"][0]["name"] == "Cyber Risk"
    assert json_data["data"]["list"][1]["name"] == "Compliance Risk"


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_empty(mock_serv, client, get_valid_token):
    """Test retrieval of business risk types with no data"""
    mock_serv.return_value = {
        "success": True,
        "message": "No Data Found.",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No Data Found."
    assert json_data["data"]["list"] == []


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_database_error(mock_serv, client, get_valid_token):
    """Test retrieval of business risk types with database error"""
    mock_serv.return_value = JSONResponse(
        content={"error": "Database connection failed"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "database connection failed" in json_data["error"].lower()


def test_get_business_risk_types_invalid_crg_id(client, get_valid_token):
    """Test retrieval of business risk types with invalid crg_id"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=invalid", headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_negative_crg_id(mock_serv, client, get_valid_token):
    """Test retrieval of business risk types with negative crg_id"""
    mock_serv.return_value = JSONResponse(
        content={"error": "Invalid crg_id"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=99999", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "invalid crg_id" in json_data["error"].lower()


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_malformed_data(mock_serv, client, get_valid_token):
    """Test retrieval of business risk types with malformed DAO response"""
    mock_serv.return_value = JSONResponse(
        content={"error": "Invalid data format"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "invalid data format" in json_data["error"].lower()


def test_get_business_risk_types_invalid_token(client):
    """Test retrieval of business risk types with missing or invalid token"""
    headers = {}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.get_business_risk_types_serv"
)
def test_get_business_risk_types_unexpected_error(mock_serv, client, get_valid_token):
    """Test get_business_risk_types with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get(
        "/v1/risk-type/get_business_risk_types?crg_id=4", headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data


# GET BUSINESS RISK TYPES ENDED

# ADD BUSINESS RISK TYPE STARTED


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_success(mock_serv, client, get_valid_token):
    """Test successful addition of business risk types"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Business Risk Types added successfully",
            "new_ids": [101, 102, 103],
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "selected_ids": [1, 2, 3], "expose_to_relevent_api": True}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Business Risk Types added successfully"
    assert json_data["new_ids"] == [101, 102, 103]


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_duplicate(mock_serv, client, get_valid_token):
    """Test adding business risk types with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "selected_ids": [1, 2], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding business risk types with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 999, "selected_ids": [1, 2], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_generic_error(mock_serv, client, get_valid_token):
    """Test adding business risk types with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "selected_ids": [1, 2], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Database integrity error"


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_empty_selected_ids(mock_serv, client, get_valid_token):
    """Test adding business risk types with empty selected_ids"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "No risk type IDs provided"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "selected_ids": [], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "No risk type IDs provided"


def test_add_business_risk_type_invalid_payload(client, get_valid_token):
    """Test adding business risk types with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "expose_to_relevent_api": False}  # Missing selected_ids
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data
    assert "selected_ids" in str(json_data["detail"]).lower()


def test_add_business_risk_type_invalid_token(client):
    """Test adding business risk types with missing or invalid token"""
    headers = {}
    payload = {"crg_id": 10, "selected_ids": [1, 2], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_type_controller.RiskTypeServices.add_business_risk_type_serv"
)
def test_add_business_risk_type_unexpected_error(mock_serv, client, get_valid_token):
    """Test add_business_risk_type with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 10, "selected_ids": [1, 2], "expose_to_relevent_api": False}
    response = client.post(
        "/v1/risk-type/add_business_risk_type", json=payload, headers=headers
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


# ADD BUSINESS RISK TYPE ENDED
