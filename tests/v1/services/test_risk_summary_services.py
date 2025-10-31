import pytest
import json
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from pydantic import BaseModel
from collections import defaultdict
import os
from ai_agents.deduplication_agent import DeduplicationEngine
from dao.v1.risk_summary_dao import RiskSummaryDAO
from services.v1.gemini_services import Gemini_Services
from services.v1.risk_summary_services import RiskSummary_Services

# from your_module import (
#     RiskSummary_Services,
#     RiskSummaryDAO,
#     Gemini_Services,
#     DeduplicationEngine,
# )  # Adjust import as needed


# Mock Pydantic models
class RiskSummaryRequest(BaseModel):
    pass  # Simplified; replace with actual fields if needed


class generateRiskSummary_BaseModel(BaseModel):
    topic: list


# * ADD RISK SUMMARY STARTED
def test_add_risk_summary_success(db_session: Session):
    # Arrange
    mock_item = Mock()
    data = [mock_item]
    current_user = {"user_id": 999}
    with patch.object(RiskSummaryDAO, "addRiskSummaryDAO", return_value=1) as mock_dao:
        # Act
        response = RiskSummary_Services.add_risk_summary_serv(
            data, db_session, None, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Risk Summary Saved."
    assert response_data["risk_summary_ids"] == [1]
    mock_dao.assert_called_once_with(mock_item, db_session, current_user)


def test_add_risk_summary_dao_failure(db_session: Session):
    # Arrange
    mock_item = Mock()
    data = [mock_item]
    current_user = {"user_id": 999}
    error_response = JSONResponse(content={"error": "DAO error"}, status_code=400)
    with patch.object(RiskSummaryDAO, "addRiskSummaryDAO", return_value=error_response):
        # Act
        response = RiskSummary_Services.add_risk_summary_serv(
            data, db_session, None, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "DAO error"


def test_add_risk_summary_general_exception(db_session: Session):
    # Arrange
    data = [Mock()]
    current_user = {"user_id": 999}
    with patch.object(
        RiskSummaryDAO, "addRiskSummaryDAO", side_effect=Exception("Test error")
    ):
        # Act
        response = RiskSummary_Services.add_risk_summary_serv(
            data, db_session, None, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "Test error"


# * ADD RISK SUMMARY ENDED


# * GET BUSINESS RISK MULTI QUESTION STARTED
def test_get_business_risk_multi_question_success(db_session: Session):
    # Arrange
    risk_summary_ids = [1]
    mock_data = Mock(business_risk="Risk A", human_rating=1)
    mock_crg_data = [1, "Category A", "Test Category"]
    with patch.object(RiskSummaryDAO, "RiskSummaryDataDAO", return_value=mock_data):
        with patch.object(RiskSummaryDAO, "getCRGID", return_value=mock_crg_data):
            # Act
            response = RiskSummary_Services.get_business_risk_multi_question_serv(
                risk_summary_ids, db_session
            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["crg_id"] == 1
    assert response_data["data"] == {
        "Test Category": [
            {"risk_summary_id": 1, "business_risk": "Risk A", "user_rating": 1}
        ]
    }


def test_get_business_risk_multi_question_non_high_rating(db_session: Session):
    # Arrange
    risk_summary_ids = [1]
    mock_data = Mock(business_risk="Risk A", human_rating=2)  # Medium rating
    mock_crg_data = [1, "Category A", "Test Category"]
    with patch.object(RiskSummaryDAO, "RiskSummaryDataDAO", return_value=mock_data):
        with patch.object(RiskSummaryDAO, "getCRGID", return_value=mock_crg_data):
            # Act
            response = RiskSummary_Services.get_business_risk_multi_question_serv(
                risk_summary_ids, db_session
            )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["data"] == {}  # No high rating, so empty


# * GET BUSINESS RISK MULTI QUESTION ENDED


# * ADD ASSERT BUSINESS RISK STARTED
def test_add_assert_business_risk_success(db_session: Session):
    # Arrange
    data = {
        "crg_id": 1,
        "data": [
            {"risk_summary_id": 1, "user_rating": 1},
            {"risk_summary_id": 2, "user_rating": 2},
        ],
    }
    current_user = {"user_id": 999}
    with patch.object(RiskSummaryDAO, "addAssertBusinessRisk", side_effect=[10, 11]):
        # Act
        response = RiskSummary_Services.add_assert_business_risk_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "All ratings processed"
    assert response_data["crg_id"] == 1
    assert response_data["results"] == [
        {
            "risk_summary_id": 1,
            "user_rating": 1,
            "success": True,
            "assert_business_risk_id": 10,
            "message": "Data added successfully",
        },
        {
            "risk_summary_id": 2,
            "user_rating": 2,
            "success": True,
            "assert_business_risk_id": 11,
            "message": "Data added successfully",
        },
    ]


# def test_add_assert_business_risk_invalid_rating(db_session: Session):
#     # Arrange
#     data = {
#         "crg_id": 1,
#         "data": [{"risk_summary_id": 1, "user_rating": 4}],  # Invalid rating
#     }
#     current_user = {"user_id": 999}

#     # Act
#     response = RiskSummary_Services.add_assert_business_risk_serv(
#         data, db_session, current_user
#     )

#     # Assert
#     assert isinstance(response, JSONResponse)
#     assert response.status_code == 400
#     response_data = json.loads(response.body.decode("utf-8"))
#     assert response_data["error"] == "Invalid rating '4' for risk_summary_id 1"


def test_add_assert_business_risk_dao_failure(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "data": [{"risk_summary_id": 1, "user_rating": 1}]}
    current_user = {"user_id": 999}
    error_response = JSONResponse(content={"error": "DAO error"}, status_code=400)
    with patch.object(
        RiskSummaryDAO, "addAssertBusinessRisk", return_value=error_response
    ):
        # Act
        response = RiskSummary_Services.add_assert_business_risk_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "DAO error"


def test_add_assert_business_risk_general_exception(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "data": [{"risk_summary_id": 1, "user_rating": 1}]}
    current_user = {"user_id": 999}
    with patch.object(
        RiskSummaryDAO, "addAssertBusinessRisk", side_effect=Exception("Test error")
    ):
        # Act
        response = RiskSummary_Services.add_assert_business_risk_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "Test error"


# * ADD ASSERT BUSINESS RISK ENDED


# * GET GENERATE ABR RECOMMENDATION STARTED
def test_get_generate_abr_recommendation_success(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "assert_business_risk_ids": [1, 2]}
    mock_abr_data = [(1, "Type A", "Risk A"), (2, "Type B", "Risk B")]
    mock_crg_details = {"some": "data"}
    mock_gemini_data = {
        "impacts": ["Impact 1"],
        "mitigation_sentences": ["Mitigation 1"],
        "how_to_mitigate": ["How to 1"],
    }
    with patch.object(
        RiskSummaryDAO, "abrRecommendationDAO", return_value=mock_abr_data
    ):
        with patch.object(
            RiskSummaryDAO, "getCRGDetailsDAO", return_value=mock_crg_details
        ):
            with patch.object(
                Gemini_Services,
                "gemini_abr_recommendation_data",
                return_value=mock_gemini_data,
            ):
                # Act
                response = RiskSummary_Services.get_generate_abr_recommendation_serv(
                    data, db_session
                )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["crg_id"] == 1
    # assert response_data["data"] == {
    #     1: {
    #         "risk_type": "Type A",
    #         "impacts": ["Impact 1"],
    #         "mitigation_strategies": ["Mitigation 1"],
    #         "how_to_mitigate": ["How to 1"],
    #     },
    #     2: {
    #         "risk_type": "Type B",
    #         "impacts": ["Impact 1"],
    #         "mitigation_strategies": ["Mitigation 1"],
    #         "how_to_mitigate": ["How to 1"],
    #     },
    # }


def test_get_generate_abr_recommendation_general_exception(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "assert_business_risk_ids": [1]}
    with patch.object(
        RiskSummaryDAO, "abrRecommendationDAO", side_effect=Exception("Test error")
    ):
        # Act
        response = RiskSummary_Services.get_generate_abr_recommendation_serv(
            data, db_session
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "Test error"


# * GET GENERATE ABR RECOMMENDATION ENDED


# * ADD ABR RECOMMENDATION STARTED
def test_add_abr_recommendation_success(db_session: Session):
    # Arrange
    data = {
        "crg_id": 1,
        "data": [
            {"business_risk_id": 1, "impacts": ["Impact 1"]},
            {"business_risk_id": 2, "impacts": ["Impact 2"]},
        ],
    }
    current_user = {"user_id": 999}
    with patch.object(RiskSummaryDAO, "AddABR_RecommendationDAO", side_effect=[10, 11]):
        # Act
        response = RiskSummary_Services.add_abr_recommendation_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["crg_id"] == 1
    assert response_data["abr_recommendation_ids"] == [10, 11]


def test_add_abr_recommendation_dao_failure(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "data": [{"business_risk_id": 1, "impacts": ["Impact 1"]}]}
    current_user = {"user_id": 999}
    error_response = JSONResponse(content={"error": "DAO error"}, status_code=400)
    with patch.object(
        RiskSummaryDAO, "AddABR_RecommendationDAO", return_value=error_response
    ):
        # Act
        response = RiskSummary_Services.add_abr_recommendation_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "DAO error"


def test_add_abr_recommendation_general_exception(db_session: Session):
    # Arrange
    data = {"crg_id": 1, "data": [{"business_risk_id": 1, "impacts": ["Impact 1"]}]}
    current_user = {"user_id": 999}
    with patch.object(
        RiskSummaryDAO, "AddABR_RecommendationDAO", side_effect=Exception("Test error")
    ):
        # Act
        response = RiskSummary_Services.add_abr_recommendation_serv(
            data, db_session, current_user
        )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["error"] == "Test error"


# * ADD ABR RECOMMENDATION ENDED


# # * GENERATE RISK SUMMARY DETAILS LLM ONLY STARTED
# @pytest.mark.asyncio
# async def test_generate_risk_summary_details_llm_only_success_development(
#     db_session: Session, monkeypatch
# ):
#     # Arrange
#     data = generateRiskSummary_BaseModel(topic=[1, 2])
#     mock_categories = ["Category A", "Category B"]
#     mock_grouped_data = {(1, "Category A"): ["Risk 1"], (2, "Category B"): ["Risk 2"]}
#     mock_gemini_data = {"1": ["Risk 1"], "2": ["Risk 2"]}
#     mock_log_entries = ["log1"]
#     mock_json_log_data = {"data": "log"}
#     monkeypatch.setenv("FASTAPI_ENV", "development")
#     with patch.object(
#         RiskSummaryDAO, "getGeminiCategoriesDAO", return_value=mock_categories
#     ):
#         with patch.object(
#             DeduplicationEngine,
#             "run_duplication_pipeline_llm_only",
#             return_value=(
#                 mock_grouped_data,
#                 mock_gemini_data,
#                 mock_log_entries,
#                 mock_json_log_data,
#             ),
#         ) as mock_dedup:
#             with patch("your_module.write_agent_using_llm_logs") as mock_write_logs:
#                 # Act
#                 response = await RiskSummary_Services.generate_risk_summary_details_llm_only_serv(
#                     data, db_session
#                 )

#     # Assert
#     assert isinstance(response, JSONResponse)
#     assert response.status_code == 200
#     response_data = json.loads(response.body.decode("utf-8"))
#     assert response_data["success"] is True
#     assert response_data["data"] == [
#         {"br_id": 1, "category": "Category A", "risks": ["Risk 1"]},
#         {"br_id": 2, "category": "Category B", "risks": ["Risk 2"]},
#     ]
#     assert response_data["real_data"] == mock_gemini_data
#     mock_dedup.assert_called_once_with([1, 2], mock_categories, db_session)
#     mock_write_logs.assert_called_once()


# @pytest.mark.asyncio
# async def test_generate_risk_summary_details_llm_only_success_non_development(
#     db_session: Session, monkeypatch
# ):
#     # Arrange
#     data = generateRiskSummary_BaseModel(topic=[1, 2])
#     mock_categories = ["Category A"]
#     mock_grouped_data = {(1, "Category A"): ["Risk 1"]}
#     mock_gemini_data = {"1": ["Risk 1"]}
#     mock_log_entries = ["log1"]
#     mock_json_log_data = {"data": "log"}
#     monkeypatch.setenv("FASTAPI_ENV", "production")
#     with patch.object(
#         RiskSummaryDAO, "getGeminiCategoriesDAO", return_value=mock_categories
#     ):
#         with patch.object(
#             DeduplicationEngine,
#             "run_duplication_pipeline_llm_only",
#             return_value=(
#                 mock_grouped_data,
#                 mock_gemini_data,
#                 mock_log_entries,
#                 mock_json_log_data,
#             ),
#         ):
#             with patch("your_module.write_agent_using_llm_logs") as mock_write_logs:
#                 # Act
#                 response = await RiskSummary_Services.generate_risk_summary_details_llm_only_serv(
#                     data, db_session
#                 )

#     # Assert
#     assert isinstance(response, JSONResponse)
#     assert response.status_code == 200
#     response_data = json.loads(response.body.decode("utf-8"))
#     assert response_data["success"] is True
#     assert response_data["data"] == [
#         {"br_id": 1, "category": "Category A", "risks": ["Risk 1"]}
#     ]
#     assert "real_data" not in response_data  # Excluded in non-development


# @pytest.mark.asyncio
# async def test_generate_risk_summary_details_llm_only_no_categories(
#     db_session: Session,
# ):
#     # Arrange
#     data = generateRiskSummary_BaseModel(topic=[1])
#     with patch.object(RiskSummaryDAO, "getGeminiCategoriesDAO", return_value=[]):
#         # Act
#         response = (
#             await RiskSummary_Services.generate_risk_summary_details_llm_only_serv(
#                 data, db_session
#             )
#         )

#     # Assert
#     assert isinstance(response, JSONResponse)
#     assert response.status_code == 400
#     response_data = json.loads(response.body.decode("utf-8"))
#     assert response_data["message"] == "No Categories Found."


# @pytest.mark.asyncio
# async def test_generate_risk_summary_details_llm_only_general_exception(
#     db_session: Session,
# ):
#     # Arrange
#     data = generateRiskSummary_BaseModel(topic=[1])
#     with patch.object(
#         RiskSummaryDAO, "getGeminiCategoriesDAO", side_effect=Exception("Test error")
#     ):
#         # Act
#         response = (
#             await RiskSummary_Services.generate_risk_summary_details_llm_only_serv(
#                 data, db_session
#             )
#         )

#     # Assert
#     assert isinstance(response, JSONResponse)
#     assert response.status_code == 400
#     response_data = json.loads(response.body.decode("utf-8"))
#     assert response_data["error"] == "Test error"


# # * GENERATE RISK SUMMARY DETAILS LLM ONLY ENDED
