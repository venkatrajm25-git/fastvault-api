import pytest
import sys
import os
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session
from database.v1.connection import getDBConnection

# Add project root to path
# print("Python sys.path:", sys.path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# print("Updated sys.path:", sys.path)


# Import FastAPI app
from main import app as fastapi_app


@pytest.fixture
def app():
    yield fastapi_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def db_session():
    """Yields a real SQLAlchemy DB session for use in ORM tests."""
    db = next(getDBConnection())  # ✅ This resolves the Depends(getDBConnection)
    try:
        yield db
    finally:
        db.close()


# @pytest.fixture
# def get_valid_token(client):
#     """Fetch a valid token for testing other APIs."""
#     response = client.post(
#         "/v1/auth/login", json={"email": "admin@gmail.com", "password": "admin@123"}
#     )
#     assert response.status_code == 200
#     token = response.json().get("token")
#     assert token is not None
#     return token  # ✅ return the actual token, not a boolean


@pytest.fixture
def get_valid_token(client):
    response = client.post(
        "/v1/auth/login",
        json={"email": "masteradmin@gmail.com", "password": "admin@321"},
    )

    assert response.status_code == 200
    token = response.cookies.get("access_token")
    assert token is not None
    return token


def get_or_create_by_name(
    db_session, model, name_field="module_name", name_value="Default"
):
    """
    Reusable utility to get or create a DB entry by a unique name.
    Example: get_or_create_by_name(db, Module, "name", "TestModule")
    """
    existing = (
        db_session.query(model).filter(getattr(model, name_field) == name_value).first()
    )
    if existing:
        return existing

    instance = model(**{name_field: name_value})
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance
