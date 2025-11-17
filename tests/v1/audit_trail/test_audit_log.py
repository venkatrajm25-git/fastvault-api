import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.responses import JSONResponse
from audit_trail.v1.audit_decorater import audit_loggable


class DummyModel:
    class ID:
        @staticmethod
        def desc():
            return "id DESC"

    id = ID()

    def __init__(self, id, name):
        self._sa_instance_state = None
        self.id = id
        self.name = name


@audit_loggable(action="CREATE", table_name="dummy_table", model_class=DummyModel)
async def create_dummy(request, db):
    db.query.return_value.order_by.return_value.first.return_value = DummyModel(
        1, "Venkat"
    )
    return JSONResponse(content={"success": True}, status_code=201)


@audit_loggable(
    action="UPDATE", table_name="dummy_table", model_class=DummyModel, id_field="id"
)
async def update_dummy(id, request, db):
    db.query.return_value.filter.return_value.first.return_value = DummyModel(
        1, "Updated Venkat"
    )
    return JSONResponse(content={"success": True}, status_code=200)


@audit_loggable(
    action="DELETE", table_name="dummy_table", model_class=DummyModel, id_field="id"
)
async def delete_dummy(id: int, request, db):
    # Simulate record to be deleted
    db.query.return_value.filter.return_value.first.return_value = DummyModel(
        id, "Delete Me"
    )
    return JSONResponse(content={"success": True}, status_code=200)


def test_create_audit_log():
    mock_db = MagicMock()
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b'{"name": "Venkat"}')

    with patch(
        "utils.v1.audit_logger.log_audit", new_callable=AsyncMock
    ) as mock_log_audit:
        response = asyncio.run(create_dummy(request=mock_request, db=mock_db))

        # Assert
        assert response.status_code == 201
        mock_log_audit.assert_called_once()

        call_args = mock_log_audit.call_args[1]  # get kwargs from the call
        assert call_args["action"] == "CREATE"
        assert call_args["table_name"] == "dummy_table"
        assert call_args["record_id"] == 1


def test_audit_log_update():
    mock_db = MagicMock()
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b'{"id": 1, "name": "Updated Venkat"}')
    mock_request.id = None

    dummy_instance = DummyModel(1, "Updated Venkat")
    with patch("utils.v1.audit_logger.log_audit", new_callable=AsyncMock) as mock_log:
        mock_db.query.return_value.filter.return_value.first.return_value = (
            dummy_instance
        )

        response = asyncio.run(update_dummy(id=1, request=mock_request, db=mock_db))

        assert response.status_code == 200
        mock_log.assert_called_once()
        assert mock_log.call_args[1]["action"] == "UPDATE"
        assert mock_log.call_args[1]["record_id"] == 1


def test_audit_log_delete():
    mock_db = MagicMock()
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b'{"id": 1}')

    with patch("utils.v1.audit_logger.log_audit", new_callable=AsyncMock) as mock_log:
        response = asyncio.run(delete_dummy(id=1, request=mock_request, db=mock_db))

        assert response.status_code == 200
        mock_log.assert_called_once()
        assert mock_log.call_args[1]["action"] == "DELETE"
