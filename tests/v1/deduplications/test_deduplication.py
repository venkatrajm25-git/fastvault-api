import json
import asyncio
from pdb import run
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.responses import JSONResponse
import numpy as np
from ai_agents.deduplication_agent import DeduplicationEngine, EmbeddingService
from services.v1.risk_summary_services import RiskSummary_Services
from schema.v1.jeeno_x_schema import generateRiskSummary_BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
)


# Test cases
@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_success_development(
    mock_get_categories,
    mock_pipeline,
    mock_write_logs,
    client,
    get_valid_token,
    monkeypatch,
):
    """Test successful risk summary generation in development mode"""
    monkeypatch.setenv("FASTAPI_ENV", "development")
    mock_get_categories.return_value = [
        {"br_id": 1, "risk_type": "Cyber"},
        {"br_id": 2, "risk_type": "Finance"},
    ]
    mock_pipeline.return_value = (
        {
            (1, "Cyber"): [
                {"business_risk": "Cyber Attack", "description": "Malware risk"}
            ],
            (2, "Finance"): [
                {"business_risk": "Fraud", "description": "Financial loss"}
            ],
        },
        [
            {
                "business_risk": "Cyber Attack",
                "description": "Malware risk",
                "br_id": 1,
                "category": "Cyber",
            },
            {
                "business_risk": "Fraud",
                "description": "Financial loss",
                "br_id": 2,
                "category": "Finance",
            },
        ],
        ["Accepted: Cyber Attack for br_id=1", "Accepted: Fraud for br_id=2"],
        [
            {
                "br_id": 1,
                "risk_title": "Cyber Attack",
                "status": "ACCEPTED",
                "similarity": 0.0,
            },
            {
                "br_id": 2,
                "risk_title": "Fraud",
                "status": "ACCEPTED",
                "similarity": 0.0,
            },
        ],
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1, 2]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 2
    assert json_data["data"][0] == {
        "br_id": 1,
        "category": "Cyber",
        "risks": [{"business_risk": "Cyber Attack", "description": "Malware risk"}],
    }
    assert json_data["data"][1] == {
        "br_id": 2,
        "category": "Finance",
        "risks": [{"business_risk": "Fraud", "description": "Financial loss"}],
    }
    assert len(json_data["real_data"]) == 2
    assert json_data["real_data"][0]["business_risk"] == "Cyber Attack"
    assert json_data["real_data"][1]["business_risk"] == "Fraud"
    mock_write_logs.assert_called_once()


@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_success_production(
    mock_get_categories,
    mock_pipeline,
    mock_write_logs,
    client,
    get_valid_token,
    monkeypatch,
):
    """Test successful risk summary generation in production mode"""
    monkeypatch.setenv("FASTAPI_ENV", "production")
    mock_get_categories.return_value = [{"br_id": 1, "risk_type": "Cyber"}]
    mock_pipeline.return_value = (
        {
            (1, "Cyber"): [
                {"business_risk": "Cyber Attack", "description": "Malware risk"}
            ]
        },
        [
            {
                "business_risk": "Cyber Attack",
                "description": "Malware risk",
                "br_id": 1,
                "category": "Cyber",
            }
        ],
        ["Accepted: Cyber Attack for br_id=1"],
        [
            {
                "br_id": 1,
                "risk_title": "Cyber Attack",
                "status": "ACCEPTED",
                "similarity": 0.0,
            }
        ],
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0] == {
        "br_id": 1,
        "category": "Cyber",
        "risks": [{"business_risk": "Cyber Attack", "description": "Malware risk"}],
    }
    assert "real_data" not in json_data
    mock_write_logs.assert_called_once()


@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_no_categories(
    mock_get_categories, client, get_valid_token
):
    """Test risk summary generation with no categories"""
    mock_get_categories.return_value = []
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [99]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["message"] == "No Categories Found."


@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_empty_risks(
    mock_get_categories, mock_pipeline, mock_write_logs, client, get_valid_token
):
    """Test risk summary generation with no risks generated"""
    mock_get_categories.return_value = [{"br_id": 1, "risk_type": "Cyber"}]
    mock_pipeline.return_value = (
        {},
        [],
        ["No risks generated for br_id=1"],
        [{"br_id": 1, "risk_title": None, "status": "NO_RISKS"}],
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] == []
    assert json_data.get("real_data", []) == []
    mock_write_logs.assert_called_once()


@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_high_similarity(
    mock_get_categories, mock_pipeline, mock_write_logs, client, get_valid_token
):
    """Test risk summary generation with high-similarity risk rejection"""
    mock_get_categories.return_value = [{"br_id": 1, "risk_type": "Cyber"}]
    mock_pipeline.return_value = (
        {
            (1, "Cyber"): [
                {"business_risk": "Cyber Attack", "description": "Malware risk"}
            ]
        },
        [
            {
                "business_risk": "Cyber Attack",
                "description": "Malware risk",
                "br_id": 1,
                "category": "Cyber",
            },
            {
                "business_risk": "Cyber Breach",
                "description": "Similar malware risk",
                "br_id": 1,
                "category": "Cyber",
            },
        ],
        [
            "Accepted: Cyber Attack for br_id=1",
            "Rejected: Cyber Breach for br_id=1 due to high similarity (0.85)",
        ],
        [
            {
                "br_id": 1,
                "risk_title": "Cyber Attack",
                "status": "ACCEPTED",
                "similarity": 0.0,
            },
            {
                "br_id": 1,
                "risk_title": "Cyber Breach",
                "status": "REJECTED",
                "similarity": 0.85,
            },
        ],
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["risks"][0]["business_risk"] == "Cyber Attack"
    assert len(json_data["real_data"]) == 2
    assert json_data["real_data"][1]["business_risk"] == "Cyber Breach"
    mock_write_logs.assert_called_once()


@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_gemini_rejection(
    mock_get_categories, mock_pipeline, mock_write_logs, client, get_valid_token
):
    """Test risk summary generation with Gemini agent rejection"""
    mock_get_categories.return_value = [{"br_id": 1, "risk_type": "Cyber"}]
    mock_pipeline.return_value = (
        {
            (1, "Cyber"): [
                {"business_risk": "Cyber Attack", "description": "Malware risk"}
            ]
        },
        [
            {
                "business_risk": "Cyber Attack",
                "description": "Malware risk",
                "br_id": 1,
                "category": "Cyber",
            },
            {
                "business_risk": "Cyber Threat",
                "description": "Similar risk",
                "br_id": 1,
                "category": "Cyber",
            },
        ],
        [
            "Accepted: Cyber Attack for br_id=1",
            "Rejected: Cyber Threat for br_id=1 by Gemini agent (TRUE_DUPLICATE)",
        ],
        [
            {
                "br_id": 1,
                "risk_title": "Cyber Attack",
                "status": "ACCEPTED",
                "similarity": 0.0,
            },
            {
                "br_id": 1,
                "risk_title": "Cyber Threat",
                "status": "REJECTED",
                "similarity": 0.70,
                "agent_decision": "TRUE_DUPLICATE",
            },
        ],
    )
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["risks"][0]["business_risk"] == "Cyber Attack"
    assert len(json_data["real_data"]) == 2
    assert json_data["real_data"][1]["business_risk"] == "Cyber Threat"
    mock_write_logs.assert_called_once()


def test_generate_risk_summary_invalid_payload(client, get_valid_token):
    """Test risk summary generation with missing topic"""
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {}  # Missing topic
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    json_data = response.json()
    assert "detail" in json_data
    assert "topic" in str(json_data["detail"]).lower()


@patch("services.v1.risk_summary_services.write_agent_logs")
@patch(
    "services.v1.risk_summary_services.DeduplicationEngine.run_duplication_pipeline",
    new_callable=AsyncMock,
)
@patch("services.v1.risk_summary_services.RiskSummaryDAO.getGeminiCategoriesDAO")
def test_generate_risk_summary_error(
    mock_get_categories, mock_pipeline, mock_write_logs, client, get_valid_token
):
    """Test risk summary generation with database or Gemini error"""
    mock_get_categories.return_value = [{"br_id": 1, "risk_type": "Cyber"}]
    mock_pipeline.side_effect = Exception("Database connection failed")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "error" in json_data
    assert "database connection failed" in json_data["error"].lower()


def test_generate_risk_summary_invalid_token(client):
    """Test risk summary generation with missing or invalid token"""
    headers = {}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    json_data = response.json()
    assert "detail" in json_data


@patch(
    "controllers.v1.risk_summary_controller.RiskSummary_Services.generate_risk_summary_details_serv"
)
def test_generate_risk_summary_unexpected_error(mock_serv, client, get_valid_token):
    """Test retrieval of risk summary with unexpected error"""
    mock_serv.side_effect = Exception("Unexpected error in service")
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    payload = {"topic": [1]}
    response = client.post(
        "/v1/risk-summary/generate-risk-summary", json=payload, headers=headers
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "detail" in json_data
    assert "unexpected error in service" in json_data["detail"].lower()


# * EMBEDDING SERVICE EMBED STARTED


def test_embed_combined_text():
    # Given test input
    business_risk = "High financial exposure"
    description = (
        "The business may lose substantial capital in case of market fluctuations."
    )
    combined_text = f"{business_risk} {description}"

    # When
    vector = EmbeddingService.embed(combined_text)

    # Then
    assert isinstance(vector, np.ndarray), "Expected output to be a NumPy array"
    assert vector.shape == (
        384,
    ), f"Expected embedding of shape (384,), got {vector.shape}"
    assert not np.all(vector == 0), "Embedding vector should not be all zeros"


# * EMBEDDING SERVICE EMBED ENDED


def test_empty_br_ids(db_session):
    """Test with empty br_ids list."""
    result = asyncio.run(
        DeduplicationEngine.run_duplication_pipeline(
            [], [{"br_id": 1, "risk_type": "type1"}], db_session
        )
    )
    assert result == ({}, [], [], [])


mock_business_risk = {"id": 1, "crg_id": 3, "risk_type_relation_id": 1, "is_deleted": 0}


@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getBusinessRiskDAO")
def test_get_business_risk_for_first_br_id(mock_get_risk, db_session):
    # Arrange
    # async def test_run_duplication_pipeline_basic(db_session):
    br_ids = [1]
    categories = [{"br_id": 1, "risk_type": "type1"}]

    # Mocking the response of RiskSummaryDAO.getBusinessRiskDAO
    mock_business_risk = MagicMock()
    mock_business_risk.expose_to_relevent_api = 1

    # with patch.object(RiskSummaryDAO, "getBusinessRiskDAO", return_value=mock_business_risk):
    result = asyncio.run(
        DeduplicationEngine.run_duplication_pipeline(br_ids, categories, db_session)
    )

    assert isinstance(result, tuple)
    assert len(result) == 4  # Expecting a tuple with 4 elements


@patch("ai_agents.deduplication_agent.cosine_similarity")
@patch("ai_agents.deduplication_agent.EmbeddingService.embed")
@patch("ai_agents.deduplication_agent.Gemini_Services.get_risk_details")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getBusinessRiskDAO")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getCRGDetailsDAO")
def test_high_similarity_rejection(
    mock_crg_details,
    mock_business_risk,
    mock_get_risk_details,
    mock_embed,
    mock_cosine_similarity,
):
    # Mock input
    br_ids = [1, 2]
    categories = [
        {"br_id": 1, "risk_type": "type1"},
        {"br_id": 2, "risk_type": "type1"},
    ]

    # Mocks
    mock_business_risk.return_value = type(
        "obj", (object,), {"expose_to_relevent_api": 1}
    )()
    mock_crg_details.return_value = {"crg": "mock_data"}
    mock_get_risk_details.return_value = [
        {
            "business_risk": "Duplicate Risk",
            "description": "High similarity description",
        },
        {"business_risk": "Duplicate Risk 2", "description": "High similarity desc 2"},
    ]
    mock_embed.return_value = np.array([0.1] * 384)
    mock_cosine_similarity.return_value = np.array([[0.85]])  # High similarity

    # Run
    grouped_data, gemini_data, log_entries, json_logs = asyncio.run(
        DeduplicationEngine.run_duplication_pipeline(br_ids, categories, db="mock_db")
    )

    # Assert
    assert len(grouped_data.get((1, "type1"), [])) == 6

    assert len(grouped_data.get((2, "type1"), [])) == 0  # Second BR rejects all
    assert all(log["status"] in ["ACCEPTED", "REJECTED"] for log in json_logs)
    assert any(
        log["status"] == "REJECTED" and log["similarity"] == 0.85 for log in json_logs
    )
    assert all(
        not log.get("agent_used") for log in json_logs if log["status"] == "REJECTED"
    )


@patch("ai_agents.deduplication_agent.Gemini_Services.get_agentic_comparison")
@patch("ai_agents.deduplication_agent.cosine_similarity")
@patch("ai_agents.deduplication_agent.EmbeddingService.embed")
@patch("ai_agents.deduplication_agent.Gemini_Services.get_risk_details")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getBusinessRiskDAO")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getCRGDetailsDAO")
def test_medium_similarity_agent_decision(
    mock_crg_details,
    mock_business_risk,
    mock_get_risk_details,
    mock_embed,
    mock_cosine_similarity,
    mock_get_agentic_comparison,
):
    # Mock input
    br_ids = [1, 2]
    categories = [
        {"br_id": 1, "risk_type": "type1"},
        {"br_id": 2, "risk_type": "type1"},
    ]

    # Mocks
    mock_business_risk.return_value = type(
        "obj", (object,), {"expose_to_relevent_api": 1}
    )()
    mock_crg_details.return_value = {"crg": "mock_data"}
    mock_get_risk_details.return_value = [
        {
            "business_risk": "Risk 1",
            "description": "Description for risk 1",
        },
        {
            "business_risk": "Similar Risk",
            "description": "Similar description",
        },
    ]
    #     mock_embed.return_value = npiatria

    # System: np.array([0.1] * 384)
    mock_embed.return_value = np.array([0.1] * 384)
    mock_cosine_similarity.return_value = np.array([[0.75]])  # Medium similarity
    mock_get_agentic_comparison.return_value = {"decision": "TRUE_DUPLICATE"}

    # Run
    grouped_data, gemini_data, log_entries, json_logs = asyncio.run(
        DeduplicationEngine.run_duplication_pipeline(br_ids, categories, db="mock_db")
    )

    # Assert
    assert len(grouped_data.get((1, "type1"), [])) == 6  # First BR accepts 5 risks
    assert (
        len(grouped_data.get((2, "type1"), [])) == 0
    )  # Second BR rejects due to similarity
    assert any(
        log["status"] == "REJECTED" and log["similarity"] == 0.75 for log in json_logs
    )
    assert any(
        log["agent_used"]
        and log["status"] == "REJECTED"
        and log["agent_decision"] == "TRUE_DUPLICATE"
        for log in json_logs
    )
    assert all(
        log["br_id"] in [1, 2] and log["risk_title"] in ["Risk 1", "Similar Risk"]
        for log in json_logs
    )


@patch("ai_agents.deduplication_agent.Gemini_Services.get_risk_details")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getBusinessRiskDAO")
@patch("ai_agents.deduplication_agent.RiskSummaryDAO.getCRGDetailsDAO")
def test_empty_risk_summary(
    mock_crg_details,
    mock_business_risk,
    mock_get_risk_details,
):
    # Mock input
    br_ids = [1]
    categories = [
        {"br_id": 1, "risk_type": "type1"},
    ]

    # Mocks
    mock_business_risk.return_value = type(
        "obj", (object,), {"expose_to_relevent_api": 1}
    )()
    mock_crg_details.return_value = {"crg": "mock_data"}
    mock_get_risk_details.return_value = []  # Simulate empty risk_summary

    # Run
    grouped_data, gemini_data, log_entries, json_logs = asyncio.run(
        DeduplicationEngine.run_duplication_pipeline(br_ids, categories, db="mock_db")
    )

    # Assert
    assert len(grouped_data.get((1, "type1"), [])) == 0  # No risks added
    assert len(gemini_data) == 0  # No data in geminiGeneratedData
    assert len(log_entries) == 0  # No log entries since no risks were processed
    assert len(json_logs) == 0  # No json log entries since no risks were processed
    mock_get_risk_details.assert_called_once_with(
        category="type1",
        relevantAPIAcceptance="Yes",
        crgDetails={"crg": "mock_data"},
        exclude_titles=[],
        count=5,
    )


# import pytest
# import asyncio
# from unittest.mock import AsyncMock, patch, MagicMock
# import numpy as np
# from ai_agents.deduplication_agent import (
#     DeduplicationEngine,
# )  # Assuming the class is in deduplication_engine.py


# @pytest.fixture
# def mock_dependencies():
#     """Set up mocks for external dependencies."""
#     # Mock RiskSummaryDAO
#     mock_risk_summary_dao = MagicMock()
#     mock_risk_summary_dao.getBusinessRiskDAO.return_value = MagicMock(
#         expose_to_relevent_api=1
#     )
#     mock_risk_summary_dao.getCRGDetailsDAO.return_value = {
#         "details": "mock_crg_details"
#     }

#     # Mock Gemini_Services
#     mock_gemini_services = MagicMock()
#     mock_gemini_services.get_risk_details.return_value = [
#         {"business_risk": "Risk 1", "description": "Description 1"},
#         {"business_risk": "Risk 2", "description": "Description 2"},
#     ]
#     mock_gemini_services.get_agentic_comparison = AsyncMock(
#         return_value={"decision": "NOT_DUPLICATE"}
#     )

#     # Mock EmbeddingService
#     mock_embedding_service = MagicMock()
#     mock_embedding_service.embed.return_value = np.array([0.1, 0.2, 0.3])

#     # Mock cosine_similarity
#     mock_cosine_similarity = MagicMock(return_value=np.array([[0.5]]))

#     # Mock AIAgentsLogSetup
#     mock_log_setup = MagicMock()
#     mock_log_setup.format_deduplication_decision.return_value = "formatted_log_entry"

#     # Apply patches
#     patches = [
#         patch(
#             "ai_agents.deduplication_agent.RiskSummaryDAO.getCRGDetailsDAO",
#             mock_risk_summary_dao,
#         ),
#         patch(
#             "ai_agents.deduplication_agent.Gemini_Services.get_risk_details",
#             mock_gemini_services,
#         ),
#         patch(
#             "ai_agents.deduplication_agent.EmbeddingService.embed",
#             mock_embedding_service,
#         ),
#         patch(
#             "ai_agents.deduplication_agent.cosine_similarity", mock_cosine_similarity
#         ),
#         patch(
#             "ai_agents.deduplication_agent.AIAgentsLogSetup.format_deduplication_decision",
#             mock_log_setup,
#         ),
#     ]
#     for p in patches:
#         p.start()

#     # Mock db object
#     mock_db = MagicMock()

#     yield {
#         "mock_risk_summary_dao": mock_risk_summary_dao,
#         "mock_gemini_services": mock_gemini_services,
#         "mock_embedding_service": mock_embedding_service,
#         "mock_cosine_similarity": mock_cosine_similarity,
#         "mock_log_setup": mock_log_setup,
#         "mock_db": mock_db,
#     }

#     # Teardown patches
#     for p in patches:
#         p.stop()

# def test_empty_categories(mock_risk_summary_dao, db_session):
#     """Test with empty categories list."""
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline([1], [], db_session)
#     )
#     assert result == (
#         {},  # grouped_data
#         [],  # geminiGeneratedData
#         [],  # logs
#         [],  # previouslyAccepted
#     )
#     mock_risk_summary_dao.getBusinessRiskDAO.assert_called_once_with(1, db_session)


# def test_single_br_id_no_risk_types(mock_dependencies):
#     """Test with a br_id that has no matching risk types."""
#     categories = [{"br_id": 2, "risk_type": "type1"}]  # No match for br_id 1
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1], categories, mock_dependencies["mock_db"]
#         )
#     )
#     assert result == (
#         {},
#         [],
#         [],
#         [],
#     )  # Expect empty grouped_data, geminiGeneratedData, logs
#     mock_dependencies[
#         "mock_risk_summary_dao"
#     ].getBusinessRiskDAO.assert_called_once_with(1, mock_dependencies["mock_db"])
#     mock_dependencies["mock_risk_summary_dao"].getCRGDetailsDAO.assert_called_once_with(
#         1, mock_dependencies["mock_db"]
#     )


# def test_first_br_id_accepts_all(mock_dependencies):
#     """Test first br_id where all risks are accepted without similarity checks."""
#     categories = [{"br_id": 1, "risk_type": "type1"}]
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert len(gemini_data) == 2  # Two risks from mock
#     assert len(grouped_data.get((1, "type1"), [])) == 2  # Both accepted
#     assert len(log_entries) == 2  # Two log entries
#     assert len(json_logs) == 2  # Two json log entries
#     assert json_logs[0]["status"] == "ACCEPTED"
#     assert json_logs[0]["similarity"] == 0.0
#     assert not json_logs[0]["agent_used"]
#     mock_dependencies[
#         "mock_cosine_similarity"
#     ].assert_not_called()  # No similarity checks for first br_id


# def test_high_similarity_rejection(mock_dependencies):
#     """Test rejection due to high cosine similarity (>0.80)."""
#     categories = [
#         {"br_id": 1, "risk_type": "type1"},
#         {"br_id": 2, "risk_type": "type1"},
#     ]
#     mock_dependencies["mock_cosine_similarity"].return_value = np.array(
#         [[0.85]]
#     )  # High similarity
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1, 2], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert len(grouped_data.get((1, "type1"), [])) == 2  # First br_id accepts all
#     assert len(grouped_data.get((2, "type1"), [])) == 0  # Second br_id rejects all
#     assert len(gemini_data) == 4  # Two risks per br_id
#     assert len(log_entries) == 4  # Two accepted, two rejected
#     assert len(json_logs) == 4
#     assert json_logs[2]["status"] == "REJECTED"
#     assert json_logs[2]["similarity"] == 0.85
#     assert not json_logs[2]["agent_used"]


# def test_medium_similarity_agent_rejection(mock_dependencies):
#     """Test medium similarity (0.70–0.80) with agent rejecting."""
#     categories = [
#         {"br_id": 1, "risk_type": "type1"},
#         {"br_id": 2, "risk_type": "type1"},
#     ]
#     mock_dependencies["mock_cosine_similarity"].return_value = np.array(
#         [[0.75]]
#     )  # Medium similarity
#     mock_dependencies["mock_gemini_services"].get_agentic_comparison.return_value = {
#         "decision": "TRUE_DUPLICATE"
#     }
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1, 2], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert len(grouped_data.get((1, "type1"), [])) == 2  # First br_id accepts all
#     assert len(grouped_data.get((2, "type1"), [])) == 0  # Second br_id rejects all
#     assert len(gemini_data) == 4  # Two risks per br_id
#     assert len(log_entries) == 4  # Two accepted, two rejected
#     assert len(json_logs) == 4
#     assert json_logs[2]["status"] == "REJECTED"
#     assert json_logs[2]["similarity"] == 0.75
#     assert json_logs[2]["agent_used"]
#     assert json_logs[2]["agent_decision"] == "TRUE_DUPLICATE"


# def test_medium_similarity_agent_acceptance(mock_dependencies):
#     """Test medium similarity (0.70–0.80) with agent accepting."""
#     categories = [
#         {"br_id": 1, "risk_type": "type1"},
#         {"br_id": 2, "risk_type": "type1"},
#     ]
#     mock_dependencies["mock_cosine_similarity"].return_value = np.array(
#         [[0.75]]
#     )  # Medium similarity
#     mock_dependencies["mock_gemini_services"].get_agentic_comparison.return_value = {
#         "decision": "NOT_DUPLICATE"
#     }
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1, 2], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert len(grouped_data.get((1, "type1"), [])) == 2  # First br_id accepts all
#     assert len(grouped_data.get((2, "type1"), [])) == 2  # Second br_id accepts all
#     assert len(gemini_data) == 4  # Two risks per br_id
#     assert len(log_entries) == 4  # Four accepted
#     assert len(json_logs) == 4
#     assert json_logs[2]["status"] == "ACCEPTED"
#     assert json_logs[2]["similarity"] == 0.75
#     assert json_logs[2]["agent_used"]
#     assert json_logs[2]["agent_decision"] == "NOT_DUPLICATE"


# def test_empty_risk_summary(mock_dependencies):
#     """Test when Gemini returns an empty risk summary."""
#     categories = [{"br_id": 1, "risk_type": "type1"}]
#     mock_dependencies["mock_gemini_services"].get_risk_details.return_value = []
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert grouped_data == {}  # No risks accepted
#     assert gemini_data == []  # No risks generated
#     assert log_entries == []  # No logs
#     assert json_logs == []  # No json logs
#     mock_dependencies["mock_gemini_services"].get_risk_details.assert_called_once()


# def test_max_attempts_reached(mock_dependencies):
#     """Test when max_total_attempts (20) is reached."""
#     categories = [{"br_id": 1, "risk_type": "type1"}]
#     mock_dependencies["mock_gemini_services"].get_risk_details.side_effect = [
#         []
#     ] * 20  # Empty responses
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, gemini_data, log_entries, json_logs = result
#     assert grouped_data == {}  # No risks accepted
#     assert gemini_data == []  # No risks generated
#     assert log_entries == []  # No logs
#     assert json_logs == []  # No json logs
#     assert mock_dependencies["mock_gemini_services"].get_risk_details.call_count == 20


# def test_relevant_api_acceptance_no(mock_dependencies):
#     """Test when expose_to_relevent_api is 0."""
#     mock_dependencies["mock_risk_summary_dao"].getBusinessRiskDAO.return_value = (
#         MagicMock(expose_to_relevent_api=0)
#     )
#     categories = [{"br_id": 1, "risk_type": "type1"}]
#     result = asyncio.run(
#         DeduplicationEngine.run_duplication_pipeline(
#             [1], categories, mock_dependencies["mock_db"]
#         )
#     )

#     grouped_data, _, _, _ = result
#     assert len(grouped_data.get((1, "type1"), [])) == 2  # Risks still accepted
#     mock_dependencies["mock_gemini_services"].get_risk_details.assert_called_once_with(
#         category="type1",
#         relevantAPIAcceptance="No",
#         crgDetails={"details": "mock_crg_details"},
#         exclude_titles=[],
#         count=5,
#     )
