from fastapi.responses import JSONResponse
import pytest
from unittest.mock import patch, Mock, MagicMock
from model.v1.risk_type_model import RiskType  # Adjust import as needed
from schema.v1.jeeno_x_schema import RiskTypeBaseModel
from services.v1.risk_type_services import RiskTypeServices
from dao.v1.risk_type_dao import RiskTypeDAO


# * GET RISK TYPE SERVICE STARTED
def test_get_risk_type_serv_success_non_empty(db_session):
    # Arrange
    mock_risk_type = Mock(id=1, risk_type="Operational Risk", status=1)
    mock_risk_types = [mock_risk_type]
    with patch.object(RiskTypeDAO, "getRiskTypeData", return_value=mock_risk_types):
        # Act
        response = RiskTypeServices.get_risk_type_serv(db_session)

    # Assert
    assert response == {
        "success": True,
        "message": "Data fetched successfully",
        "data": {"list": [{"id": 1, "name": "Operational Risk", "status": 1}]},
    }


def test_get_risk_type_serv_empty(db_session):
    # Arrange
    with patch.object(RiskTypeDAO, "getRiskTypeData", return_value=[]):
        # Act
        response = RiskTypeServices.get_risk_type_serv(db_session)

    # Assert
    assert response == {
        "success": True,
        "message": "No risk-types found",
        "data": {"list": []},
    }


# * ADD RISK TYPE STARTED


def test_add_risk_type_serv_success():
    data = RiskTypeBaseModel(risk_type="Tech Risk", status=1)
    db = MagicMock()
    current_user = {"user_id": 42}

    with patch("dao.v1.risk_type_dao.RiskTypeDAO.addRiskType", return_value=99):
        response = RiskTypeServices.add_risk_type_serv(data, db, current_user)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    content = response.body.decode("utf-8")
    assert "Data Added Successfully" in content
    assert '"Risk Type ID":99' in content


def test_add_risk_type_serv_failure():
    data = RiskTypeBaseModel(risk_type="Duplicate", status=1)
    db = MagicMock()
    current_user = {"user_id": 42}

    error_response = JSONResponse(content={"error": "Duplicate entry"}, status_code=400)

    with patch(
        "dao.v1.risk_type_dao.RiskTypeDAO.addRiskType", return_value=error_response
    ):
        response = RiskTypeServices.add_risk_type_serv(data, db, current_user)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    content = response.body.decode("utf-8")
    assert "Duplicate entry" in content


# * ADD RISK TYPE ENDED


from unittest.mock import patch, MagicMock
from services.v1.risk_type_services import RiskTypeServices  # adjust as per your code


class MockRiskType:
    def __init__(self, id, risk_governance_id, risk_type_id, status):
        self.id = id
        self.risk_governance_id = risk_governance_id
        self.risk_type_id = risk_type_id
        self.status = status


@patch("dao.v1.risk_type_dao.RiskTypeDAO.getRiskGovernanceTypeData")
def test_get_risk_governance_risktype_serv_success(mock_dao):
    # Arrange: mock data with 2 records
    mock_dao.return_value = [
        MockRiskType(1, 100, 200, 1),
        MockRiskType(2, 101, 201, 1),
    ]

    db = MagicMock()

    # Act
    result = RiskTypeServices.get_risk_governance_risktype_serv(db)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"


@patch("dao.v1.risk_type_dao.RiskTypeDAO.getRiskGovernanceTypeData")
def test_get_risk_governance_risktype_serv_empty(mock_dao):
    # Arrange: mock empty list
    mock_dao.return_value = []

    db = MagicMock()

    # Act
    result = RiskTypeServices.get_risk_governance_risktype_serv(db)

    # Assert
    assert result["success"] is True
    assert result["message"] == "No Risk Governance - Risk Types found"
    assert result["data"]["list"] == []


@patch("dao.v1.risk_type_dao.RiskTypeDAO.getBusinessRiskTypesData")
def test_get_business_risk_types_serv_success(mock_dao):
    # Arrange
    mock_dao.return_value = [(1, "Tech Risk"), (2, "Regulatory Risk")]
    db = MagicMock()

    # Act
    result = RiskTypeServices.get_business_risk_types_serv(crg_id=10, db=db)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Data fetched successfully"
    assert result["data"]["list"][0]["name"] == "Tech Risk"


@patch("dao.v1.risk_type_dao.RiskTypeDAO.getBusinessRiskTypesData")
def test_get_business_risk_types_serv_no_data(mock_dao):
    # Arrange
    mock_dao.return_value = []
    db = MagicMock()

    # Act
    result = RiskTypeServices.get_business_risk_types_serv(crg_id=10, db=db)

    # Assert
    assert result["success"] is True
    assert result["message"] == "No Data Found."
    assert result["data"]["list"] == []


@patch("dao.v1.risk_type_dao.RiskTypeDAO.getBusinessRiskTypesData")
def test_get_business_risk_types_serv_exception(mock_dao):
    # Arrange: Force exception
    mock_dao.side_effect = Exception("DB error")
    db = MagicMock()

    # Act
    result = RiskTypeServices.get_business_risk_types_serv(crg_id=10, db=db)

    # Assert
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert "DB error" in result.body.decode("utf-8")


class DummyData:
    def __init__(self, crg_id, selected_ids):
        self.crg_id = crg_id
        self.selected_ids = selected_ids


@patch("dao.v1.risk_type_dao.RiskTypeDAO.addBusinessRiskTypeDAO")
def test_add_business_risk_type_serv_success(mock_dao):
    # Arrange
    mock_dao.return_value = {"success": True, "message": "Added"}
    db = MagicMock()
    current_user = {"user_id": 42}
    data = DummyData(crg_id=1, selected_ids=[101, 102])

    # Act
    result = RiskTypeServices.add_business_risk_type_serv(data, db, current_user)

    # Assert
    assert result["success"] is True
    assert result["message"] == "Added"


@patch("dao.v1.risk_type_dao.RiskTypeDAO.addBusinessRiskTypeDAO")
def test_add_business_risk_type_serv_error(mock_dao):
    # Arrange
    error_response = JSONResponse(content={"error": "Invalid input"}, status_code=400)
    mock_dao.return_value = error_response

    db = MagicMock()
    current_user = {"user_id": 42}
    data = DummyData(crg_id=1, selected_ids=[999])

    # Act
    result = RiskTypeServices.add_business_risk_type_serv(data, db, current_user)

    # Assert
    assert isinstance(result, JSONResponse)
    assert result.status_code == 400
    assert "Invalid input" in result.body.decode("utf-8")
