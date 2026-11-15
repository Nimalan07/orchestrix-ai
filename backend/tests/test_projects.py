import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.session import Base, get_db


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_create_project(client):
    response = client.post(
        "/api/projects",
        json={
            "name": "Orchestrix Test",
            "description": "Testing project creation API functionality."
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Orchestrix Test"
    assert data["status"] == "created"
    assert "id" in data


def test_list_projects(client):
    client.post(
        "/api/projects",
        json={
            "name": "Project One",
            "description": "Testing project listing functionality."
        }
    )
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_project(client):
    response = client.post(
        "/api/projects",
        json={
            "name": "AB",
            "description": "Short"
        }
    )
    assert response.status_code == 422


def test_nonexistent_project(client):
    response = client.get(
        "/api/projects/invalid-project-id"
    )
    assert response.status_code == 404


def test_update_project(client):
    created = client.post(
        "/api/projects",
        json={
            "name": "Original Project",
            "description": "Testing project update functionality."
        }
    )
    project_id = created.json()["id"]
    response = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"


def test_delete_project(client):
    created = client.post(
        "/api/projects",
        json={
            "name": "Delete Me",
            "description": "Testing project deletion functionality."
        }
    )
    project_id = created.json()["id"]
    response = client.delete(
        f"/api/projects/{project_id}"
    )
    assert response.status_code == 204
    response = client.get(
        f"/api/projects/{project_id}"
    )
    assert response.status_code == 404
