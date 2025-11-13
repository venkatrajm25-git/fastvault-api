import pytest
import sys
import os
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session

# ✅ Step 1: Add project root to sys.path *before* any local imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ✅ Step 2: Import app AFTER path fix
from main import app as fastapi_app
from database.v1.connection import getDBConnection


# ✅ Step 3: Fixtures
@pytest.fixture
def app():
    """Yields the FastAPI app instance"""
    yield fastapi_app


@pytest.fixture
def client(app):
    """Returns a TestClient instance bound to our FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fake():
    """Returns a Faker instance"""
    return Faker()


@pytest.fixture
def db_session():
    """Yields a real SQLAlchemy DB session for ORM tests"""
    db = next(getDBConnection())  # resolves Depends(getDBConnection)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def get_valid_token(client):
    """Fetch a valid token for testing authenticated endpoints"""
    response = client.post(
        "/v1/auth/login",
        json={"email": "masteradmin@gmail.com", "password": "admin@321"},
    )
    print("\n[DEBUG] /v1/auth/login response:", response.status_code, response.text)
    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.cookies.get("access_token")
    assert token is not None, "No access token returned"
    return token


def get_or_create_by_name(db_session, model, name_field="name", name_value="Default"):
    """
    Utility to get or create a DB record by a unique name.
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
