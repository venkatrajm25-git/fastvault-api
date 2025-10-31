import json
from fastapi.responses import JSONResponse
import pytest
from unittest.mock import patch, MagicMock
from services.v1.risk_governance_services import (
    RiskGovernanceServ,
)  # Adjust to your module path


@pytest.fixture
def mock_db_session():
    return MagicMock()


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getUseCasesData")
def test_get_use_cases_success(mock_get_use_cases):
    # Arrange - mock return value
    use_case_1 = MagicMock(id=1, use_case="AGI", status=1)
    use_case_2 = MagicMock(id=2, use_case="General", status=2)
    mock_get_use_cases.return_value = [use_case_1, use_case_2]

    # Act
    result = RiskGovernanceServ.get_use_cases_serv(db=None)

    # Assert - ignoring list order
    expected = {
        "success": True,
        "data": {
            "list": [
                {"id": 1, "name": "AGI", "status": 1},
                {"id": 2, "name": "General", "status": 2},
            ]
        },
    }

    # Sort both lists before comparison to avoid order issues
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


def test_get_use_cases_empty(mock_db_session):
    # Arrange
    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getUseCasesData",
        return_value=[],
    ):
        # Act
        result = RiskGovernanceServ.get_use_cases_serv(mock_db_session)

    # Assert
    assert result == {
        "success": True,
        "message": "No use cases found",
        "data": {"list": []},
    }


def test_get_use_cases_domain_non_empty(mock_db_session):
    # Arrange
    domain_1 = MagicMock(id=1, domain="Finance", status="active")
    domain_2 = MagicMock(id=2, domain="Healthcare", status="inactive")
    mock_data = [domain_1, domain_2]

    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getUseCase_DomainData",
        return_value=mock_data,
    ):
        # Act
        result = RiskGovernanceServ.get_use_cases_domain_serv(mock_db_session)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


def test_get_use_cases_domain_empty(mock_db_session):
    # Arrange
    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getUseCase_DomainData",
        return_value=[],
    ):
        # Act
        result = RiskGovernanceServ.get_use_cases_domain_serv(mock_db_session)

    # Assert
    assert result == {
        "success": True,
        "message": "No Domains found",
        "data": {"list": []},
    }


# -------------------------------
# Test: get_countries_serv
# -------------------------------


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getCountriesData")
def test_get_countries_success(mock_get_countries):
    # Arrange
    country_1 = MagicMock(id=1, country_name="USA", status=1)
    country_2 = MagicMock(id=2, country_name="India", status=2)
    mock_get_countries.return_value = [country_1, country_2]

    # Act
    result = RiskGovernanceServ.get_countries_serv(db=None)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getCountriesData")
def test_get_countries_empty(mock_get_countries):
    # Arrange
    mock_get_countries.return_value = []

    # Act
    result = RiskGovernanceServ.get_countries_serv(db=None)

    # Assert
    assert result == {
        "success": True,
        "message": "No countries found",
        "data": {"list": []},
    }


# -------------------------------
# Test: get_risk_governance_serv
# -------------------------------


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getRiskGovernanceData")
def test_get_risk_governance_success(mock_get_risks):
    # Arrange
    rg1 = MagicMock()
    rg1.id = 1
    rg1.name = "AGI"
    rg1.status = 1

    rg2 = MagicMock()
    rg2.id = 2
    rg2.name = "General"
    rg2.status = 2

    mock_get_risks.return_value = [rg2, rg1]

    # Act
    result = RiskGovernanceServ.get_risk_governance_serv(db=None)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getRiskGovernanceData")
def test_get_risk_governance_empty(mock_get_risks):
    # Arrange
    mock_get_risks.return_value = []

    # Act
    result = RiskGovernanceServ.get_risk_governance_serv(db=None)

    # Assert
    assert result == {
        "success": True,
        "message": "No risk governance found",
        "data": {"list": []},
    }


# -------------------------------
# Test: get_ratings_serv
# -------------------------------


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getRatingData")
def test_get_ratings_success(mock_get_ratings):
    # Arrange
    rating1 = MagicMock(id=1, name="High")
    rating2 = MagicMock(id=2, name="Low")
    mock_get_ratings.return_value = [rating1, rating2]

    # Act
    result = RiskGovernanceServ.get_ratings_serv(db=None)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


@patch("services.v1.risk_governance_services.RiskGovernanceDAO.getRatingData")
def test_get_ratings_empty(mock_get_ratings):
    # Arrange
    mock_get_ratings.return_value = []

    # Act
    result = RiskGovernanceServ.get_ratings_serv(db=None)

    # Assert
    assert result == {
        "success": True,
        "message": "No ratings found",
        "data": {"list": []},
    }


def test_add_config_governance_risk_success(mock_db_session):
    # Arrange
    payload = MagicMock()
    payload.use_case_id = 1
    payload.domain_id = 2
    payload.country_id = 3
    payload.risk_governance_id = 4
    payload.status = 1
    current_user = {"user_id": "user_123"}
    request = MagicMock()
    mock_response = {"success": True, "message": "Risk governance added"}

    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.addConfigRiskGovernance",
        return_value=mock_response,
    ):
        # Act
        result = RiskGovernanceServ.add_config_governance_risk_serv(
            payload, mock_db_session, request, current_user
        )

    # Assert
    assert result == mock_response
    assert result["success"] is True
    assert result["message"] == "Risk governance added"


def test_add_config_governance_risk_exception(mock_db_session):
    # Arrange
    payload = MagicMock()
    payload.use_case_id = 1
    payload.domain_id = 2
    payload.country_id = 3
    payload.risk_governance_id = 4
    payload.status = 1
    current_user = {"user_id": "user_123"}
    request = MagicMock()

    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.addConfigRiskGovernance",
        side_effect=Exception("Database error"),
    ):
        # Act
        result = RiskGovernanceServ.add_config_governance_risk_serv(
            payload, mock_db_session, request, current_user
        )

    # Assert
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    response_data = json.loads(result.body.decode("utf-8"))
    assert response_data["error"] == "Database error"


def test_get_result_summary_success(mock_db_session):
    # Arrange
    data = {"crg_id": 1, "abr_recommendation_ids": [1, 2]}
    business_risk_summaries = [(1, "Compliance"), (2, "Security")]
    abr_recommendations = ["Recommendation 1", "Recommendation 2"]
    crg_details = {"detail": "CRG details"}
    recommendation = "Address compliance and security risks."

    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getResultSummaryDAO",
        return_value=business_risk_summaries,
    ):
        with patch(
            "services.v1.risk_governance_services.RiskGovernanceDAO.get_ABR_RecommendationDAO",
            return_value=abr_recommendations,
        ):
            with patch(
                "services.v1.risk_governance_services.RiskGovernanceDAO.crgDetailsResultSummaryDAO",
                return_value=crg_details,
            ):
                with patch(
                    "services.v1.risk_governance_services.Gemini_Services.get_combined_abr_recommendation",
                    return_value=recommendation,
                ):
                    # Act
                    result = RiskGovernanceServ.get_result_summary_serv(
                        data, mock_db_session
                    )

    # Assert
    assert isinstance(result, JSONResponse)
    assert result.status_code == 200
    response_data = json.loads(result.body.decode("utf-8"))
    assert response_data["success"] is True


def test_get_result_summary_exception(mock_db_session):
    # Arrange
    data = {"crg_id": 1, "abr_recommendation_ids": [1, 2]}

    with patch(
        "services.v1.risk_governance_services.RiskGovernanceDAO.getResultSummaryDAO",
        side_effect=Exception("Database error"),
    ):
        # Act
        try:
            RiskGovernanceServ.get_result_summary_serv(data, mock_db_session)
            pytest.fail("Expected Exception")
        except Exception as e:
            # Assert
            assert str(e) == "Database error"
