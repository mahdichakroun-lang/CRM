"""
Test configuration — Sets up a test client with SQLite in-memory database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.shared.security import hash_password
from app.domain.auth.models import User, UserRole

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client with fresh DB."""
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def admin_token(client, db):
    """Create an admin user and return a valid JWT token."""
    user = User(
        name="Test Admin",
        email="testadmin@crm.local",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "testadmin@crm.local",
        "password": "admin123",
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Authorization headers with admin JWT."""
    return {"Authorization": f"Bearer {admin_token}"}
