import json
from unittest.mock import patch
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from model.v1.risk_governance_model import UseCaseModel


# GET USE CASES STARTED


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_use_cases_serv"
)
def test_get_use_cases_empty(mock_serv, client, get_valid_token, db_session):
    """Test fetching use cases when none exist"""
    # Ensure no use cases exist
    mock_serv.return_value = {
        "success": True,
        "message": "No use cases found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_use_cases", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No use cases found"
    assert json_data["data"]["list"] == []


def test_get_use_cases_success(client, get_valid_token, db_session):
    """Test fetching multiple use cases with sorting"""

    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_use_cases", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"


def test_get_use_cases_database_error(client, get_valid_token):
    """Test fetching use cases with a database error"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getUseCasesData",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.get("/v1/get_use_cases", headers=headers)

        assert response.status_code == HTTP_400_BAD_REQUEST
        json_data = response.json()
        assert "detail" in json_data
        assert "database connection failed" in json_data["detail"].lower()


def test_get_use_cases_invalid_token(client):
    """Test fetching use cases with missing or invalid token"""
    headers = {}
    response = client.get("/v1/get_use_cases", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET USE CASES ENDED


# GET USE CASE DOMAIN STARTED
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_use_cases_domain_serv"
)
def test_get_use_case_domain_empty(mock_serv, client, get_valid_token):
    """Test fetching use case domains when none exist"""
    mock_serv.return_value = {
        "success": True,
        "message": "No Domains found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_use_cases_domain", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No Domains found"
    assert json_data["data"]["list"] == []


def test_get_use_case_domain_success(client, get_valid_token):
    """Test fetching multiple use case domains"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_use_cases_domain", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"


# Additional test cases
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_use_cases_domain_serv"
)
def test_get_use_case_domain_database_error(mock_serv, client, get_valid_token):
    """Test fetching use case domains with a database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_use_cases_domain", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_use_case_domain_invalid_token(client):
    """Test fetching use case domains with missing or invalid token"""
    headers = {}
    response = client.get("/v1/get_use_cases_domain", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET USE CASE DOMAIN ENDED

# GET COUNTRIES STARTED


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_countries_serv"
)
def test_get_countries_empty(mock_serv, client, get_valid_token):
    """Test fetching countries when none exist"""
    mock_serv.return_value = {
        "success": True,
        "message": "No countries found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/get_countries", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No countries found"
    assert json_data["data"]["list"] == []


def test_get_countries_success(client, get_valid_token):
    """Test fetching multiple countries"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/get_countries", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_countries_serv"
)
def test_get_countries_database_error(mock_serv, client, get_valid_token):
    """Test fetching countries with a database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("v1/get_countries", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_countries_invalid_token(client):
    """Test fetching countries with missing or invalid token"""
    headers = {}
    response = client.get("v1/get_countries", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET COUNTRIES ENDED

# GET RISK GOVERNANCE STARTED


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_risk_governance_serv"
)
def test_get_risk_governance_empty(mock_serv, client, get_valid_token):
    """Test fetching risk governance when none exist"""
    mock_serv.return_value = {
        "success": True,
        "message": "No risk governance found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_risk_governance", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No risk governance found"
    assert json_data["data"]["list"] == []


def test_get_risk_governance_success(client, get_valid_token):
    """Test fetching multiple risk governance entries with sorting"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_risk_governance", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"


# Additional test cases
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_risk_governance_serv"
)
def test_get_risk_governance_database_error(mock_serv, client, get_valid_token):
    """Test fetching risk governance with a database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_risk_governance", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_risk_governance_invalid_token(client):
    """Test fetching risk governance with missing or invalid token"""
    headers = {}
    response = client.get("/v1/get_risk_governance", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET RISK GOVERNANCE ENDED


# GET RATINGS STARTED
def test_get_ratings_success(client, get_valid_token):
    """Test successful retrieval of ratings with data"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_ratings", headers=headers)
    print(response.text)
    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data fetched successfully"


@patch("controllers.v1.risk_governance_controller.RiskGovernanceServ.get_ratings_serv")
def test_get_ratings_no_data(mock_serv, client, get_valid_token):
    """Test retrieval of ratings with no data"""
    mock_serv.return_value = {
        "success": True,
        "message": "No ratings found",
        "data": {"list": []},
    }
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_ratings", headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "No ratings found"
    assert json_data["data"]["list"] == []


@patch("controllers.v1.risk_governance_controller.RiskGovernanceServ.get_ratings_serv")
def test_get_ratings_database_error(mock_serv, client, get_valid_token):
    """Test retrieval of ratings with database error"""
    mock_serv.side_effect = RuntimeError("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_ratings", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


@patch("controllers.v1.risk_governance_controller.RiskGovernanceServ.get_ratings_serv")
def test_get_ratings_unexpected_error(mock_serv, client, get_valid_token):
    """Test retrieval of ratings with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.get("/v1/get_ratings", headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "unexpected error in service" in json_data["detail"].lower()


def test_get_ratings_invalid_token(client):
    """Test retrieval of ratings with missing or invalid token"""
    headers = {}
    response = client.get("/v1/get_ratings", headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET RATINGS ENDED


# ADD CONFIG GOVERNANCE RISK STARTED


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_config_governance_risk_serv"
)
def test_add_config_governance_risk_success(mock_serv, client, get_valid_token):
    """Test successful addition of config governance risk"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Data added successfully",
            "crg_id": 99,
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Data added successfully"
    assert json_data["crg_id"] == 99


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_config_governance_risk_serv"
)
def test_add_config_governance_risk_duplicate(mock_serv, client, get_valid_token):
    """Test adding config governance risk with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert "Duplicate entry" in json_data["error"]


# Additional test cases
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_config_governance_risk_serv"
)
def test_add_config_governance_risk_foreign_key(mock_serv, client, get_valid_token):
    """Test adding config governance risk with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert "Foreign key not existed" in json_data["error"]


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_config_governance_risk_serv"
)
def test_add_config_governance_risk_database_error(mock_serv, client, get_valid_token):
    """Test adding config governance risk with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert "Database integrity error" in json_data["error"]


def test_add_config_governance_risk_invalid_payload(client, get_valid_token):
    """Test adding config governance risk with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "use_case_id": 1,
        # Missing domain_id, country_id, risk_governance_id, status
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data
    assert "field required" in str(json_data["detail"]).lower()


def test_add_config_governance_risk_invalid_token(client):
    """Test adding config governance risk with missing or invalid token"""
    headers = {}
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_config_governance_risk_serv"
)
def test_add_config_governance_risk_unexpected_error(
    mock_serv, client, get_valid_token
):
    """Test retrieval of ratings with unexpected error"""
    payload = {
        "use_case_id": 1,
        "domain_id": 2,
        "country_id": 3,
        "risk_governance_id": 4,
        "status": 1,
    }
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.post(
        "/v1/add_config_governance_risk", json=payload, headers=headers
    )

    assert response.status_code == 500
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


# ADD CONFIG GOVERNANCE RISK ENDED


# GET RESULT SUMMARY STARTED


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_result_summary_serv"
)
def test_get_result_summary_success(mock_serv, client, get_valid_token):
    """Test successful retrieval of result summary"""
    mock_serv.return_value = JSONResponse(
        content={
            "crg_id": 123,
            "success": True,
            "recommendation": "Based on your selected risk ratings, proceeding with the use case poses significant risk to your organization, This is the combined impact from Gemini. It is advised to address this risk before moving forward with the use case.",
            "Summaries": [
                {"Question": "Your business risk appetite is High for Privacy."},
                {"Question": "Your business risk appetite is High for Security."},
            ],
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 123, "abr_recommendation_ids": [1, 2, 3]}
    response = client.post("/v1/get_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 123
    assert "This is the combined impact from Gemini." in json_data["recommendation"]
    assert len(json_data["Summaries"]) == 2
    assert (
        json_data["Summaries"][0]["Question"]
        == "Your business risk appetite is High for Privacy."
    )
    assert (
        json_data["Summaries"][1]["Question"]
        == "Your business risk appetite is High for Security."
    )


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_result_summary_serv"
)
def test_get_result_summary_empty_summaries(mock_serv, client, get_valid_token):
    """Test retrieval of result summary with no business risk summaries"""
    mock_serv.return_value = JSONResponse(
        content={
            "crg_id": 123,
            "success": True,
            "recommendation": "Based on your selected risk ratings, proceeding with the use case poses significant risk to your organization, This is the combined impact from Gemini. It is advised to address this risk before moving forward with the use case.",
            "Summaries": [],
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 123, "abr_recommendation_ids": [1, 2, 3]}
    response = client.post("/v1/get_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 123
    assert "This is the combined impact from Gemini." in json_data["recommendation"]
    assert json_data["Summaries"] == []


def test_get_result_summary_invalid_payload(client, get_valid_token):
    """Test retrieval of result summary with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 123}  # Missing abr_recommendation_ids
    response = client.post("/v1/get_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "abr_recommendation_ids" in str(json_data["detail"]).lower()


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.get_result_summary_serv"
)
def test_get_result_summary_database_error(mock_serv, client, get_valid_token):
    """Test retrieval of result summary with database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 123, "abr_recommendation_ids": [1, 2, 3]}
    response = client.post("/v1/get_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


def test_get_result_summary_invalid_token(client):
    """Test retrieval of result summary with missing or invalid token"""
    headers = {}
    payload = {"crg_id": 123, "abr_recommendation_ids": [1, 2, 3]}
    response = client.post("/v1/get_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET RESULT SUMMARY ENDED


# ADD RESULT SUMMARY STARTED
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_result_summary_serv"
)
def test_add_result_summary_success(mock_serv, client, get_valid_token):
    """Test successful addition of result summary"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Result summary added successfully.",
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "recommendation": "Enable AI controls"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Result summary added successfully."


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_result_summary_serv"
)
def test_add_result_summary_duplicate_entry(mock_serv, client, get_valid_token):
    """Test adding result summary with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "recommendation": "Duplicate data"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_result_summary_serv"
)
def test_add_result_summary_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding result summary with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 999, "recommendation": "Non-existent crg_id"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


# Additional test cases
@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_result_summary_serv"
)
def test_add_result_summary_database_error(mock_serv, client, get_valid_token):
    """Test adding result summary with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "recommendation": "Enable AI controls"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Database integrity error"


def test_add_result_summary_invalid_payload(client, get_valid_token):
    """Test adding result summary with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1}  # Missing recommendation
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "recommendation" in str(json_data["error"]).lower()


def test_add_result_summary_invalid_token(client):
    """Test adding result summary with missing or invalid token"""
    headers = {}
    payload = {"crg_id": 1, "recommendation": "Enable AI controls"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_governance_controller.RiskGovernanceServ.add_result_summary_serv"
)
def test_add_result_summary_unexpected_error(mock_serv, client, get_valid_token):
    """Test retrieval of ratings with unexpected error"""
    payload = {"crg_id": 1, "recommendation": "Enable AI controls"}
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = client.post("/v1/add_result_summary", json=payload, headers=headers)

    assert response.status_code == 500
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


# ADD RESULT SUMMARY ENDED
