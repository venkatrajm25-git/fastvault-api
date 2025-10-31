from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
import pytest
from tests.v1.conftest import db_session, get_or_create_by_name
from dao.v1.risk_summary_dao import RiskSummaryDAO
from schema.v1.jeeno_x_schema import RiskSummaryCreate
from model.v1.risk_type_model import BusinessRiskType
from model.v1.risk_summary_model import (
    RiskSummary,
    AssertBusinessRisk,
    ABRRecommendation,
)
from datetime import datetime


# Fixture for mock database session
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Fixture for mock current_user
@pytest.fixture
def mock_current_user():
    return {"user_id": "1"}


# Test getBusinessRiskDAO
def test_get_business_risk_dao_success(db_session):
    """Test successful retrieval of BusinessRiskType"""

    # Try getting existing record
    br_data = (
        db_session.query(BusinessRiskType)
        .filter(BusinessRiskType.is_deleted == 0)
        .first()
    )
    temp_created = False

    if not br_data:
        # Insert temporary data
        br_data = BusinessRiskType(
            crg_id=999,
            risk_type_relation_id=999,
            expose_to_relevent_api=1,
            is_deleted=0,
        )
        db_session.add(br_data)
        db_session.commit()
        db_session.refresh(br_data)
        temp_created = True

    # Call DAO
    result = RiskSummaryDAO.getBusinessRiskDAO(br_data.id, db_session)

    assert result is not None
    assert result.id == br_data.id
    assert result.crg_id == br_data.crg_id
    assert result.risk_type_relation_id == br_data.risk_type_relation_id
    assert result.expose_to_relevent_api == br_data.expose_to_relevent_api

    # Cleanup temporary data
    if temp_created:
        db_session.delete(br_data)
        db_session.commit()


def test_get_business_risk_dao_exception(mock_db):
    """Test getBusinessRiskDAO when an exception is raised"""
    # Simulate exception on db.query()
    mock_db.query.side_effect = Exception("Simulated DB Error")

    result = RiskSummaryDAO.getBusinessRiskDAO(1, mock_db)

    assert result == []


def test_get_risk_summary_data_success(db_session):
    """Integration test: fetch risk summaries or insert if none exist"""

    br_id = 1  # use a unique business_risk_type_id to avoid conflict

    # Step 1: Check if data exists
    existing = (
        db_session.query(RiskSummary)
        .filter(RiskSummary.business_risk_type_id == br_id, RiskSummary.is_deleted == 0)
        .all()
    )

    # Step 2: If not exist, insert one
    if not existing:
        new_summary = RiskSummary(
            business_risk_type_id=br_id,
            business_risk="Test risk summary",
            description="Test description",
            default_ai_rating=1,
            human_rating=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(new_summary)
        db_session.commit()

    # Step 3: Call DAO
    result = RiskSummaryDAO.getRiskSummaryData(br_id, db_session)

    # Step 4: Assert
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(rs.business_risk_type_id == br_id for rs in result)


# Test getGeminiCategoriesDAO
def test_get_gemini_categories_dao_success(mock_db):
    """Test successful retrieval of Gemini categories"""
    mock_row = MagicMock(br_id=1, risk_type="Operational")
    mock_db.execute.return_value.fetchall.return_value = [mock_row]
    result = RiskSummaryDAO.getGeminiCategoriesDAO([1, 2], mock_db)
    assert result == [{"br_id": 1, "risk_type": "Operational"}]
    mock_db.execute.assert_called_once()


def test_get_gemini_categories_dao_exception(mock_db):
    """Test retrieval with unexpected exception"""
    mock_db.execute.side_effect = Exception("Database error")
    result = RiskSummaryDAO.getGeminiCategoriesDAO([1, 2], mock_db)
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert result.body.decode() == '{"success":"false","error":"Database error"}'


# Test addRiskSummaryDAO
def test_add_risk_summary_dao_success(mock_db, mock_current_user):
    """Test successful addition of RiskSummary"""
    data = RiskSummaryCreate(
        business_risk_type_id=1,
        business_risk="Test Risk",
        description="Test Description",
        default_ai_rating=5,
        human_rating=4,
    )
    mock_risk_summary = MagicMock(id=1)
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 1)
    result = RiskSummaryDAO.addRiskSummaryDAO(data, mock_db, mock_current_user)
    assert result == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_add_risk_summary_dao_general_exception(mock_db, mock_current_user):
    """Test addition with unexpected exception"""
    data = RiskSummaryCreate(
        business_risk_type_id=1,
        business_risk="Test Risk",
        description="Test Description",
        default_ai_rating=5,
        human_rating=4,
    )
    mock_db.add.side_effect = Exception("Database error")
    result = RiskSummaryDAO.addRiskSummaryDAO(data, mock_db, mock_current_user)
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert result.body.decode() == '{"success":false,"error":"Database error"}'


# Test getCRGDetailsDAO
def test_get_crg_details_dao_success(mock_db):
    """Test successful retrieval of CRG details"""
    mock_row = MagicMock(
        use_case="Test Case", domain="Finance", country_name="India", name="Governance"
    )
    mock_db.execute.return_value.fetchone.return_value = mock_row
    result = RiskSummaryDAO.getCRGDetailsDAO(1, mock_db)
    assert result == mock_row
    mock_db.execute.assert_called_once()


def test_get_crg_details_dao_no_results(mock_db):
    """Test retrieval with no results"""
    mock_db.execute.return_value.fetchone.return_value = None
    result = RiskSummaryDAO.getCRGDetailsDAO(999, mock_db)
    assert result is None
    mock_db.execute.assert_called_once()


# Test RiskSummaryDataDAO
def test_risk_summary_data_dao_success(db_session):
    """Test successful retrieval of RiskSummary by rs_id"""

    # Check if there's a non-deleted RiskSummary record
    existing_risk_summary = (
        db_session.query(RiskSummary).filter(RiskSummary.is_deleted == 0).first()
    )

    # Create one if not found
    temp_created = False
    if not existing_risk_summary:
        # Also ensure a valid BusinessRiskType exists
        business_risk_type = (
            db_session.query(BusinessRiskType)
            .filter(BusinessRiskType.is_deleted == 0)
            .first()
        )
        if not business_risk_type:
            business_risk_type = BusinessRiskType(
                crg_id=999,
                risk_type_relation_id=999,
                expose_to_relevent_api=1,
                is_deleted=0,
            )
            db_session.add(business_risk_type)
            db_session.commit()
            db_session.refresh(business_risk_type)

        # Create RiskSummary
        existing_risk_summary = RiskSummary(
            business_risk_type_id=business_risk_type.id,
            business_risk="Sample risk",
            description="Sample description",
            default_ai_rating=1,
            human_rating=1,
            created_by=1,
            is_deleted=0,
        )
        db_session.add(existing_risk_summary)
        db_session.commit()
        db_session.refresh(existing_risk_summary)
        temp_created = True

    # Call the DAO method
    result = RiskSummaryDAO.RiskSummaryDataDAO(existing_risk_summary.id, db_session)

    assert result is not None
    assert isinstance(result, RiskSummary)
    assert result.id == existing_risk_summary.id

    # Cleanup if test data was added
    if temp_created:
        db_session.delete(existing_risk_summary)
        db_session.commit()


def test_risk_summary_data_dao_not_found(mock_db):
    """Test retrieval with non-existent rs_id"""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = RiskSummaryDAO.RiskSummaryDataDAO(999, mock_db)
    assert result is None


# Test addAssertBusinessRisk
def test_add_assert_business_risk_success(mock_db):
    """Test successful addition of AssertBusinessRisk"""
    data_list = [1, 2, "High", "Medium", "Low", "1"]
    mock_abr = MagicMock(id=1)
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 1)
    result = RiskSummaryDAO.addAssertBusinessRisk(data_list, mock_db)
    assert result == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_add_assert_business_risk_general_exception(mock_db):
    """Test addition with unexpected exception"""
    data_list = [1, 2, "High", "Medium", "Low", "1"]
    mock_db.add.side_effect = Exception("Database error")
    result = RiskSummaryDAO.addAssertBusinessRisk(data_list, mock_db)
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert result.body.decode() == '{"success":false,"error":"Database error"}'


# Test getCRGID
def test_get_crg_id_success(mock_db):
    """Test successful retrieval of CRG ID and risk type"""
    mock_row = MagicMock(crg_id=1, risk_type_id=2, risk_type="Operational")
    mock_db.execute.return_value.fetchone.return_value = mock_row
    result = RiskSummaryDAO.getCRGID(1, mock_db)
    assert result == mock_row
    mock_db.execute.assert_called_once()


def test_get_crg_id_no_results(mock_db):
    """Test retrieval with no results"""
    mock_db.execute.return_value.fetchone.return_value = None
    result = RiskSummaryDAO.getCRGID(999, mock_db)
    assert result is None
    mock_db.execute.assert_called_once()


# Test abrRecommendationDAO
def test_abr_recommendation_dao_success(mock_db):
    """Test successful retrieval of ABR recommendations"""
    mock_row = MagicMock(id=1, risk_type="Operational", business_risk="Test Risk")
    mock_db.execute.return_value.fetchall.return_value = [mock_row]
    result = RiskSummaryDAO.abrRecommendationDAO([1, 2], mock_db)
    assert result == [mock_row]
    mock_db.execute.assert_called_once()


def test_abr_recommendation_dao_single_id(mock_db):
    """Test retrieval with single ABR ID"""
    mock_row = MagicMock(id=1, risk_type="Operational", business_risk="Test Risk")
    mock_db.execute.return_value.fetchall.return_value = [mock_row]
    result = RiskSummaryDAO.abrRecommendationDAO(1, mock_db)
    assert result == [mock_row]
    mock_db.execute.assert_called_once()


def test_abr_recommendation_dao_no_results(mock_db):
    """Test retrieval with no results"""
    mock_db.execute.return_value.fetchall.return_value = []
    result = RiskSummaryDAO.abrRecommendationDAO([999], mock_db)
    assert result == []
    mock_db.execute.assert_called_once()


# Test AddABR_RecommendationDAO
def test_add_abr_recommendation_dao_success():
    # Arrange
    mock_db = MagicMock()
    crg_id = 6
    business_risk_id = 21
    impacts = '["Risk 1", "Risk 2"]'
    created_by = 1  # any user ID

    # Create mock return object with .id
    mock_rec = MagicMock(id=4)  # assuming new id will be 4
    mock_db.add.side_effect = lambda obj: setattr(obj, "id", 4)
    mock_db.commit.return_value = None
    mock_db.flush.return_value = None

    # Act
    result = RiskSummaryDAO.AddABR_RecommendationDAO(
        crg_id, business_risk_id, impacts, mock_db, created_by
    )

    # Assert
    assert result == 4
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.flush.assert_called_once()


def test_add_abr_recommendation_dao_general_exception(mock_db, mock_current_user):
    """Test addition with unexpected exception"""
    crg_id, business_risk_id, impacts, created_by = (
        1,
        1,
        "Test Impact",
        mock_current_user["user_id"],
    )
    mock_db.add.side_effect = Exception("Database error")
    result = RiskSummaryDAO.AddABR_RecommendationDAO(
        crg_id, business_risk_id, impacts, mock_db, created_by
    )
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert result.body.decode() == '{"success":false,"error":"Database error"}'
