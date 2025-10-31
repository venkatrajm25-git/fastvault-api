from sympy import true
from model.v1.risk_governance_model import ConfigRiskGovernance, ResultSummary
from model.v1.risk_summary_model import ABRRecommendation
from dao.v1.risk_governance_dao import RiskGovernanceDAO  # adjust if it's another DAO
from dao.v1.risk_summary_dao import RiskSummaryDAO

from fastapi.responses import JSONResponse
import json
from sqlalchemy import text


def test_add_config_risk_governance_success(db_session):
    # Arrange - unique test data
    test_data = [6, 3, 35, 5, 1, 999]  # dummy created_by

    # Act
    response = RiskGovernanceDAO.addConfigRiskGovernance(test_data, db_session)

    # Assert response success
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201

    # Decode response body manually
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Data added successfully"

    added_id = response_data["crg_id"]

    # Cleanup - delete test record
    db_session.query(ConfigRiskGovernance).filter_by(id=added_id).delete()
    db_session.commit()


def test_add_config_risk_governance_exception_invalid_fk(db_session):
    test_data = [9999, 3, 35, 5, 1, 999]

    # Act
    response = RiskGovernanceDAO.addConfigRiskGovernance(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    data = response.body.decode()
    assert "success" in data and "Foreign key" in data or "error" in data


# * ABR RECOMMENDATION STARTED


def test_get_abr_recommendation_dao_success(db_session):
    # Arrange: add two ABRRecommendation records (if not already in DB)
    abr_1 = ABRRecommendation(
        crg_id=6,
        business_risk_type_id=21,
        impacts=json.dumps(["Impact 1 from test", "Another test impact"]),
        created_by=999,
        is_deleted=0,
    )
    abr_2 = ABRRecommendation(
        crg_id=6,
        business_risk_type_id=21,
        impacts=json.dumps(["Impact 2 from test", "One more test impact"]),
        created_by=999,
        is_deleted=0,
    )

    db_session.add_all([abr_1, abr_2])
    db_session.commit()

    # IDs of added records
    ids = [abr_1.id, abr_2.id]

    # Act
    result = RiskGovernanceDAO.get_ABR_RecommendationDAO(ids, db_session)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(
        isinstance(row, list) for row in result
    )  # because .all() returns list of rows

    # Check that at least one known impact is there
    assert (
        "Impact 1 from test" in result[0][0][0]
        or "Impact 2 from test" in result[1][0][0]
    )

    # Cleanup
    db_session.query(ABRRecommendation).filter(ABRRecommendation.id.in_(ids)).delete(
        synchronize_session=False
    )
    db_session.commit()


# * ABR RECOMMENDATION ENDED

# * GET RESULT SUMMARY STARTED


def test_get_result_summary_dao_success(db_session):
    # --------- Setup ---------
    test_inserted = False
    inserted_id = None

    data = db_session.query(ResultSummary).first()
    if data:
        crg_id = data.crg_id
    else:
        new_result_summary = ResultSummary(
            crg_id=1, brief_summary="testing", created_by=1, is_deleted=0
        )
        db_session.add(new_result_summary)
        db_session.commit()
        db_session.refresh(new_result_summary)
        crg_id = new_result_summary.crg_id
        inserted_id = new_result_summary.id
        test_inserted = True

    # --------- Action ---------
    response = RiskGovernanceDAO.getResultSummaryDAO(crg_id, db_session)

    # --------- Assertion ---------
    assert response is not None
    assert isinstance(response, list)
    for row in response:
        assert hasattr(row, "assert_business_risk_id")
        assert hasattr(row, "business_risk")
        assert isinstance(row.assert_business_risk_id, int)
        assert isinstance(row.business_risk, str)

    # --------- Cleanup ---------
    if test_inserted and inserted_id:
        db_session.query(ResultSummary).filter_by(id=inserted_id).delete()
        db_session.commit()


# * GET RESULT SUMMARY ENDED


# * GET CRG DETAILS RESULT SUMMARY STARTED
def test_crg_details_result_summary_success(db_session):
    crg_id = 1

    # Call the DAO method
    response = RiskGovernanceDAO.crgDetailsResultSummaryDAO(crg_id, db_session)

    # Assertions
    assert response is not None, "Expected data but got None"
    assert len(response) == 4, "Expected 4 fields: use_case, domain, country_name, name"

    # Validate types of each field (optional, for stricter validation)
    use_case, domain, country_name, rg_name = response
    assert isinstance(use_case, str), "use_case should be a string"
    assert isinstance(domain, str), "domain should be a string"
    assert isinstance(country_name, str), "country_name should be a string"
    assert isinstance(rg_name, str), "risk_governance name should be a string"


# * GET CRG DETAILS RESULT SUMMARY ENDED


# * ADD RESULT SUMMARY STARTED


def test_add_result_summary_success(db_session):
    data = {"crg_id": 1, "recommendation": "testing_recommendation"}
    current_user = {"user_id": 1}

    response = RiskGovernanceDAO.addResultSummaryDAO(data, db_session, current_user)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 201

    json_data = json.loads(response.body.decode("utf-8"))  # ✅ Fix here
    assert json_data["success"] is True
    assert json_data["message"] == "Result summary added successfully."


# * ADD RESULT SUMMARY ENDED
