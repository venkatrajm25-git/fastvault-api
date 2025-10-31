import json
from unittest.mock import MagicMock
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dao.v1.risk_type_dao import RiskTypeDAO
from model.v1.risk_type_model import (
    RiskType,
    RiskGovernanceRiskType,
    BusinessRiskType,
)  # Adjust import as needed
import pytest
from pydantic import BaseModel

from routes.v1.risk_type_route import add_risk_type


# Test for getRiskTypeData
def test_get_risk_type_data_success(db_session: Session):
    # Arrange: Add a test RiskType record
    test_risk_type = RiskType(
        risk_type="Test Risk", status=1, created_by=1, is_deleted=0
    )
    db_session.add(test_risk_type)
    db_session.commit()
    db_session.refresh(test_risk_type)

    # Act
    result = RiskTypeDAO.getRiskTypeData(db_session)

    # Assert
    assert isinstance(result, list)
    assert len(result) >= 1
    assert any(r.risk_type == "Test Risk" for r in result)

    # Cleanup
    db_session.query(RiskType).filter(RiskType.id == test_risk_type.id).delete()
    db_session.commit()


# Test for addRiskType (success case)
def test_add_risk_type_success(db_session: Session):
    # Arrange
    test_data = ["Test Risk", 1, 1]  # risk_type, status, created_by

    # Act
    response = RiskTypeDAO.addRiskType(test_data, db_session)

    # Assert
    assert isinstance(response, int)  # Returns new ID on success
    assert response > 0

    # Verify record in DB
    added_risk = db_session.query(RiskType).filter(RiskType.id == response).first()
    assert added_risk is not None
    assert added_risk.risk_type == "Test Risk"

    # Cleanup
    db_session.query(RiskType).filter(RiskType.id == response).delete()
    db_session.commit()


# Test for addRiskType (duplicate entry error)
def test_add_risk_type_duplicate_entry(db_session: Session):
    # Arrange: Add a RiskType first
    test_risk_type = RiskType(
        risk_type="Duplicate Risk", status=1, created_by=1, is_deleted=0
    )
    db_session.add(test_risk_type)
    db_session.commit()

    test_data = ["Duplicate Risk", 1, 1]  # Same risk_type to trigger duplicate error

    # Act
    response = RiskTypeDAO.addRiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Duplicate entry"

    # Cleanup
    db_session.query(RiskType).filter(RiskType.risk_type == "Duplicate Risk").delete()
    db_session.commit()


def test_add_risk_type_foreign_key_contraint(db_session: Session):

    test_data = ["Duplicate Risk", 50, 1]  # status - foreign key failure

    # Act
    response = RiskTypeDAO.addRiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Foreign key not existed."


# Test for getRiskGovernanceTypeData
def test_get_risk_governance_type_data_success(db_session: Session):
    # Arrange: Add a test RiskGovernanceRiskType record
    test_rg_rt = RiskGovernanceRiskType(
        risk_governance_id=1, risk_type_id=1, status=1, created_by=1, is_deleted=0
    )
    db_session.add(test_rg_rt)
    db_session.commit()

    # Act
    result = RiskTypeDAO.getRiskGovernanceTypeData(db_session)

    # Assert
    assert isinstance(result, list)
    assert len(result) >= 1
    assert any(r.risk_governance_id == 1 for r in result)

    # Cleanup
    db_session.query(RiskGovernanceRiskType).filter(
        RiskGovernanceRiskType.id == test_rg_rt.id
    ).delete()
    db_session.commit()


# Test for addRiskGoverance_RiskType (success case)
def test_add_risk_governance_risk_type_success(db_session: Session):
    # Arrange
    test_data = [1, 1, 1, 1]  # risk_governance_id, risk_type_id, status, created_by

    # Act
    response = RiskTypeDAO.addRiskGoverance_RiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Risk Governance - Risk Type added successfully."

    # Cleanup: Delete the added record
    db_session.query(RiskGovernanceRiskType).filter(
        RiskGovernanceRiskType.risk_governance_id == 1,
        RiskGovernanceRiskType.risk_type_id == 1,
    ).delete()
    db_session.commit()


def test_add_risk_governance_risk_type_duplicate_entry(db_session: Session):
    # Arrange: Insert a RiskGovernanceRiskType record to trigger duplicate error
    data = (
        db_session.query(RiskGovernanceRiskType)
        .filter(
            RiskGovernanceRiskType.risk_governance_id == 1,
            RiskGovernanceRiskType.risk_type_id == 1,
        )
        .first()
    )
    if not data:
        test_rg_rt = RiskGovernanceRiskType(
            risk_governance_id=1, risk_type_id=1, status=1, created_by=999, is_deleted=0
        )
        db_session.add(test_rg_rt)
        db_session.commit()

    test_data = [
        1,
        1,
        1,
        1,
    ]  # Same risk_governance_id and risk_type_id to trigger duplicate error

    # Act
    response = RiskTypeDAO.addRiskGoverance_RiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    result = json.loads(response.body.decode("utf-8"))
    assert result["success"] is False
    assert result["error"] == "Duplicate entry"

    # Cleanup
    db_session.query(RiskGovernanceRiskType).filter(
        RiskGovernanceRiskType.risk_governance_id == 1,
        RiskGovernanceRiskType.risk_type_id == 1,
    ).delete()
    db_session.commit()


# * ADD RISK GOVERNANCE RISK TYPE DUPLICATE ENTRY ENDED


# * ADD RISK GOVERNANCE RISK TYPE FOREIGN KEY CONSTRAINT STARTED
def test_add_risk_governance_risk_type_foreign_key_constraint(db_session: Session):
    # Arrange: Use invalid risk_governance_id or risk_type_id to trigger foreign key error
    test_data = [
        9999,
        1,
        1,
        1,
    ]  # Invalid risk_governance_id (assumes 9999 does not exist)

    # Act
    response = RiskTypeDAO.addRiskGoverance_RiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Foreign key not existed."

    # Cleanup: None needed as no record was added


# * ADD RISK GOVERNANCE RISK TYPE FOREIGN KEY CONSTRAINT ENDED


def test_add_risk_governance_risk_type_integrity_error():
    # Simulate a NOT NULL constraint violation
    orig_exception = Exception(
        "null value in column 'risk_type_id' violates not-null constraint"
    )
    integrity_error = IntegrityError("IntegrityError", params=None, orig=orig_exception)

    mock_db = MagicMock()
    mock_db.commit.side_effect = integrity_error  # Commit will raise the IntegrityError

    # Now call the DAO directly
    response = RiskTypeDAO.addRiskGoverance_RiskType(dataList=[1, 2, 1, 1], db=mock_db)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert b"Database integrity error" in response.body


# * ADD RISK GOVERNANCE RISK TYPE GENERAL EXCEPTION STARTED
def test_add_risk_governance_risk_type_general_exception(db_session: Session):
    # Arrange: Use invalid data to trigger a general exception (e.g., invalid data type for risk_governance_id)
    test_data = ["invalid_id", 1, 1, 1]  # Non-integer risk_governance_id

    # Act
    response = RiskTypeDAO.addRiskGoverance_RiskType(test_data, db_session)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert "error" in response_data


# Test for getBusinessRiskTypesData
def test_get_business_risk_types_data_success(db_session: Session):
    # Arrange: Assume related tables (config_risk_governance, risk_governance_risk_type, risk_type) have data
    # If needed, insert test data into all three tables (simplified here)
    # data = (
    #     db_session.query(RiskType).filter(RiskType.risk_type == "Business Risk").first()
    # )
    # if not data:
    #     test_risk_type = RiskType(
    #         risk_type="Business Risk", status=1, created_by=1, is_deleted=0
    #     )
    #     db_session.add(test_risk_type)
    #     db_session.commit()
    #     db_session.refresh(test_risk_type)
    #     data = test_risk_type

    # Act
    result = RiskTypeDAO.getBusinessRiskTypesData(crg_id=1, db=db_session)

    # Assert
    assert isinstance(result, list), "Result should be a list"
    # assert len(result) >= 1, "Result should contain at least one record"
    # assert any(
    #     row.risk_type == "Business Risk" for row in result
    # ), "Result should contain 'Business Risk'"


# Test for addBusinessRiskTypeDAO (success case)
def test_add_business_risk_type_success(db_session: Session):
    # Arrange
    from pydantic import (
        BaseModel,
    )  # Assuming BusinessRiskTypeSelection_BaseModel is a Pydantic model

    class BusinessRiskTypeSelection_BaseModel(BaseModel):
        crg_id: int
        selected_ids: list
        expose_to_relevent_api: bool

    test_data = BusinessRiskTypeSelection_BaseModel(
        crg_id=1, selected_ids=[1, 2], expose_to_relevent_api=True
    )
    current_user = {"user_id": 1}

    # Act
    response = RiskTypeDAO.addBusinessRiskTypeDAO(test_data, db_session, current_user)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is True
    assert response_data["message"] == "Business Risk Types added successfully"
    assert "new_ids" in response_data
    assert len(response_data["new_ids"]) == 2

    # Cleanup
    db_session.query(BusinessRiskType).filter(BusinessRiskType.crg_id == 1).delete()
    db_session.commit()


def test_add_business_risk_type_general_exception(db_session: Session, monkeypatch):
    # Arrange: Define a mock BusinessRiskTypeSelection_BaseModel with valid data
    class BusinessRiskTypeSelection_BaseModel(BaseModel):
        crg_id: int
        selected_ids: list
        expose_to_relevent_api: bool

    test_data = BusinessRiskTypeSelection_BaseModel(
        crg_id=1,  # Valid integer to pass Pydantic validation
        selected_ids=[1, 2],  # Valid list
        expose_to_relevent_api=True,
    )
    current_user = {"user_id": 999}

    # Simulate a database error by mocking db.add_all to raise an exception
    def mock_add_all(*args, **kwargs):
        raise Exception("Simulated database error")

    monkeypatch.setattr(db_session, "add_all", mock_add_all)

    # Act
    response = RiskTypeDAO.addBusinessRiskTypeDAO(test_data, db_session, current_user)

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = json.loads(response.body.decode("utf-8"))
    assert response_data["success"] is False
    assert response_data["error"] == "Simulated database error"
