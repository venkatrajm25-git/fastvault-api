import json
import re
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from services.v1.risk_summary_services import RiskSummary_Services
from schema.v1.jeeno_x_schema import RiskSummaryRequest, RiskSummaryCreate
from controllers.v1.risk_summary_controller import RiskSummary_Controller
import asyncio
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


# ADD RISK SUMMARY STARTED
@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_risk_summary_serv"
)
def test_add_risk_summary_success(mock_serv, client, get_valid_token):
    """Test successful addition of risk summaries"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "Risk Summary Saved.",
            "risk_summary_ids": [101, 102],
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk_type_id": 1,
                "business_risk": "Test 1",
                "description": "Risk 1",
                "default_ai_rating": 3,
                "human_rating": 2,
            },
            {
                "business_risk_type_id": 2,
                "business_risk": "Test 2",
                "description": "Risk 2",
                "default_ai_rating": 1,
                "human_rating": 3,
            },
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Risk Summary Saved."
    assert json_data["risk_summary_ids"] == [101, 102]


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_risk_summary_serv"
)
def test_add_risk_summary_duplicate_error(mock_serv, client, get_valid_token):
    """Test adding risk summaries with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk_type_id": 1,
                "business_risk": "Duplicate Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_risk_summary_serv"
)
def test_add_risk_summary_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding risk summaries with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk_type_id": 999,
                "business_risk": "Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_risk_summary_serv"
)
def test_add_risk_summary_database_error(mock_serv, client, get_valid_token):
    """Test adding risk summaries with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk_type_id": 1,
                "business_risk": "Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Database integrity error"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_risk_summary_serv"
)
def test_add_risk_summary_unexpected_error(mock_serv, client, get_valid_token):
    """Test add_risk_summary with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk_type_id": 1,
                "business_risk": "Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


def test_add_risk_summary_invalid_payload(client, get_valid_token):
    """Test adding risk summaries with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [
            {
                "business_risk": "Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }  # Missing business_risk_type_id
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_add_risk_summary_empty_list(client, get_valid_token):
    """Test adding risk summaries with empty data list"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"data": []}
    response = client.post("/v1/risk-summary/add_risk_summary", headers=headers)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data


def test_add_risk_summary_invalid_token(client):
    """Test adding risk summaries with missing or invalid token"""
    headers = {}
    payload = {
        "data": [
            {
                "business_risk_type_id": 1,
                "business_risk": "Test",
                "description": "Risk",
                "default_ai_rating": 3,
                "human_rating": 2,
            }
        ]
    }
    response = client.post(
        "/v1/risk-summary/add_risk_summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# ADD RISK SUMMARY ENDED


# GET BUSINESS RISK MULTI QUESTION STARTED


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_business_risk_multi_question_serv"
)
def test_risk_summary_multi_question_success(mock_serv, client, get_valid_token):
    """Test successful retrieval of risk summary multi-question with High ratings"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "crg_id": 3,
            "data": {
                "Technology": [
                    {
                        "risk_summary_id": 101,
                        "business_risk": "Cybersecurity breach",
                        "user_rating": 1,
                    }
                ]
            },
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": [101, 102]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 3
    assert "Technology" in json_data["data"]
    assert len(json_data["data"]["Technology"]) == 1
    assert json_data["data"]["Technology"][0]["business_risk"] == "Cybersecurity breach"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_business_risk_multi_question_serv"
)
def test_risk_summary_multi_question_no_high_ratings(
    mock_serv, client, get_valid_token
):
    """Test retrieval with no High ratings"""
    mock_serv.return_value = JSONResponse(
        content={"success": True, "crg_id": 3, "data": {}}, status_code=200
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": [102, 103]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 3
    assert json_data["data"] == {}


def test_risk_summary_multi_question_empty_ids(client, get_valid_token):
    """Test retrieval with empty risk_summary_ids"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": []}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()


def test_risk_summary_multi_question_invalid_payload(client, get_valid_token):
    """Test retrieval with invalid payload (missing risk_summary_ids)"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {}  # Missing risk_summary_ids
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST

    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_business_risk_multi_question_serv"
)
def test_risk_summary_multi_question_database_error(mock_serv, client, get_valid_token):
    """Test retrieval with database error"""
    mock_serv.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": [101]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_business_risk_multi_question_serv"
)
def test_risk_summary_multi_question_unexpected_error(
    mock_serv, client, get_valid_token
):
    """Test retrieval with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": [101]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "unexpected error in service" in json_data["detail"].lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_business_risk_multi_question_serv"
)
def test_risk_summary_multi_question_malformed_data(mock_serv, client, get_valid_token):
    """Test retrieval with malformed DAO response"""
    mock_serv.side_effect = AttributeError("Invalid data format")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"risk_summary_ids": [101]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "invalid data format" in json_data["detail"].lower()


def test_risk_summary_multi_question_invalid_token(client):
    """Test retrieval with missing or invalid token"""
    headers = {}
    payload = {"risk_summary_ids": [101]}
    response = client.post(
        "/v1/risk-summary/risk_summary_multi_questions", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET BUSINESS RISK MULTI QUESTION ENDED


# ADD ASSERT BUSINESS RISK STARTED


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_success(mock_serv, client, get_valid_token):
    """Test successful addition of assert business risks"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "message": "All ratings processed",
            "crg_id": 1,
            "created_by": 1,
            "results": [
                {
                    "risk_summary_id": 10,
                    "user_rating": 1,
                    "success": True,
                    "assert_business_risk_id": 501,
                    "message": "Data added successfully",
                },
                {
                    "risk_summary_id": 11,
                    "user_rating": 3,
                    "success": True,
                    "assert_business_risk_id": 502,
                    "message": "Data added successfully",
                },
            ],
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 1,
        "data": [
            {"risk_summary_id": 10, "user_rating": 1},
            {"risk_summary_id": 11, "user_rating": 3},
        ],
    }
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "All ratings processed"
    assert json_data["crg_id"] == 1
    assert json_data["created_by"] == 1
    assert len(json_data["results"]) == 2
    assert json_data["results"][0]["user_rating"] == 1
    assert json_data["results"][1]["user_rating"] == 3


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_duplicate_error(mock_serv, client, get_valid_token):
    """Test adding assert business risks with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": [{"risk_summary_id": 10, "user_rating": 1}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding assert business risks with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 999, "data": [{"risk_summary_id": 10, "user_rating": 1}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_database_error(mock_serv, client, get_valid_token):
    """Test adding assert business risks with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": [{"risk_summary_id": 10, "user_rating": 1}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Database integrity error"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_invalid_rating(mock_serv, client, get_valid_token):
    """Test adding assert business risks with invalid user_rating"""
    mock_serv.return_value = JSONResponse(
        content={"error": "Invalid rating '4' for risk_summary_id 10"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": [{"risk_summary_id": 10, "user_rating": 4}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["error"] == "Invalid rating '4' for risk_summary_id 10"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_empty_data(mock_serv, client, get_valid_token):
    """Test adding assert business risks with empty data list"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "No data provided"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": []}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "No data provided"


def test_add_assert_business_risk_invalid_payload(client, get_valid_token):
    """Test adding assert business risks with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"data": [{"risk_summary_id": 10, "user_rating": 1}]}  # Missing crg_id
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "crg_id" in str(json_data["error"]).lower()


def test_add_assert_business_risk_missing_risk_summary_id(client, get_valid_token):
    """Test adding assert business risks with missing risk_summary_id in data"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": [{"user_rating": 1}]}  # Missing risk_summary_id
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "risk_summary_id" in str(json_data["error"]).lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_assert_business_risk_serv"
)
def test_add_assert_business_risk_unexpected_error(mock_serv, client, get_valid_token):
    """Test adding assert business risks with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 1, "data": [{"risk_summary_id": 10, "user_rating": 1}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


def test_add_assert_business_risk_invalid_token(client):
    """Test adding assert business risks with missing or invalid token"""
    headers = {}
    payload = {"crg_id": 1, "data": [{"risk_summary_id": 10, "user_rating": 1}]}
    response = client.post(
        "/v1/risk-summary/add_assert_business_risk", json=payload, headers=headers
    )
    print("response", response.text)
    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# ADD ASSERT BUSINESS RISK ENDED


# GET GENERATED ABR RECOMMENDATION STARTED


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_success(mock_serv, client, get_valid_token):
    """Test successful retrieval of ABR recommendations"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "crg_id": 99,
            "data": {
                "1": {
                    "risk_type": "Tech Risk",
                    "impacts": ["impact 1", "impact 2"],
                    "mitigation_strategies": ["mitigation 1", "mitigation 2"],
                    "how_to_mitigate": ["step 1", "step 2"],
                },
                "2": {
                    "risk_type": "Compliance Risk",
                    "impacts": ["impact 3"],
                    "mitigation_strategies": ["mitigation 3"],
                    "how_to_mitigate": ["step 3"],
                },
            },
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [1, 2], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 99
    assert "1" in json_data["data"]
    assert json_data["data"]["1"]["risk_type"] == "Tech Risk"
    assert json_data["data"]["1"]["impacts"] == ["impact 1", "impact 2"]
    assert "2" in json_data["data"]
    assert json_data["data"]["2"]["risk_type"] == "Compliance Risk"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_empty_ids(mock_serv, client, get_valid_token):
    """Test retrieval with empty assert_business_risk_ids"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "No assert business risk IDs provided"},
        status_code=400,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "No assert business risk IDs provided"


def test_get_generate_abr_recommendation_invalid_payload(client, get_valid_token):
    """Test retrieval with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 99}  # Missing assert_business_risk_ids
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "assert_business_risk_ids" in str(json_data["error"]).lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_database_error(
    mock_serv, client, get_valid_token
):
    """Test retrieval with database error"""
    mock_serv.side_effect = RuntimeError("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [1], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "database connection failed" in json_data["detail"].lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_unexpected_error(
    mock_serv, client, get_valid_token
):
    """Test retrieval with unexpected error"""
    mock_serv.side_effect = RuntimeError("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [1], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "unexpected error in service" in json_data["detail"].lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_malformed_dao_response(
    mock_serv, client, get_valid_token
):
    """Test retrieval with malformed DAO response"""
    mock_serv.side_effect = ValueError("Invalid DAO response format")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [1], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "invalid dao response format" in json_data["detail"].lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.get_generate_abr_recommendation_serv"
)
def test_get_generate_abr_recommendation_empty_gemini_response(
    mock_serv, client, get_valid_token
):
    """Test retrieval with empty Gemini service response"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "crg_id": 99,
            "data": {
                "1": {
                    "risk_type": "Tech Risk",
                    "impacts": [],
                    "mitigation_strategies": [],
                    "how_to_mitigate": [],
                }
            },
        },
        status_code=200,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"assert_business_risk_ids": [1], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 99
    assert json_data["data"]["1"]["impacts"] == []
    assert json_data["data"]["1"]["mitigation_strategies"] == []
    assert json_data["data"]["1"]["how_to_mitigate"] == []


def test_get_generate_abr_recommendation_invalid_token(client):
    """Test retrieval with missing or invalid token"""
    headers = {}
    payload = {"assert_business_risk_ids": [1], "crg_id": 99}
    response = client.post(
        "/v1/risk-summary/generate-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# GET GENERATED ASR RECOMMENDATION ENDED


# ADD ASR RECOMMENDATION STARTED


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_success(mock_serv, client, get_valid_token):
    """Test successful addition of ABR recommendations"""
    mock_serv.return_value = JSONResponse(
        content={
            "success": True,
            "crg_id": 101,
            "abr_recommendation_ids": [1001, 1002],
        },
        status_code=201,
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 101,
        "data": [
            {"business_risk_id": 1, "impacts": "Monitor activity"},
            {"business_risk_id": 2, "impacts": "Strengthen controls"},
        ],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["crg_id"] == 101
    assert json_data["abr_recommendation_ids"] == [1001, 1002]


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_empty_data(mock_serv, client, get_valid_token):
    """Test adding ABR recommendations with empty data list"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "No data provided"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"crg_id": 101, "data": []}
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "No data provided"


def test_add_abr_recommendation_invalid_payload(client, get_valid_token):
    """Test adding ABR recommendations with missing required fields"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}]
    }  # Missing crg_id
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "crg_id" in str(json_data["error"]).lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_duplicate_error(mock_serv, client, get_valid_token):
    """Test adding ABR recommendations with duplicate entry"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Duplicate entry"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 101,
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Duplicate entry"


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_foreign_key_error(mock_serv, client, get_valid_token):
    """Test adding ABR recommendations with foreign key constraint failure"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Foreign key not existed."}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 999,
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Foreign key not existed."


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_database_error(mock_serv, client, get_valid_token):
    """Test adding ABR recommendations with general database error"""
    mock_serv.return_value = JSONResponse(
        content={"success": False, "error": "Database integrity error"}, status_code=400
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 101,
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"] == "Database integrity error"


def test_add_abr_recommendation_missing_business_risk_id(client, get_valid_token):
    """Test adding ABR recommendations with missing business_risk_id in data"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 101,
        "data": [{"impacts": "Monitor activity"}],  # Missing business_risk_id
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "business_risk_id" in str(json_data["error"]).lower()


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.add_abr_recommendation_serv"
)
def test_add_abr_recommendation_unexpected_error(mock_serv, client, get_valid_token):
    """Test adding ABR recommendations with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {
        "crg_id": 101,
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert "error" in json_data
    assert "unexpected error in service" in json_data["error"].lower()


def test_add_abr_recommendation_invalid_token(client):
    """Test adding ABR recommendations with missing or invalid token"""
    headers = {}
    payload = {
        "crg_id": 101,
        "data": [{"business_risk_id": 1, "impacts": "Monitor activity"}],
    }
    response = client.post(
        "/v1/risk-summary/add-abr-recommendation", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


# ADD ASR RECOMMENDATION ENDED
