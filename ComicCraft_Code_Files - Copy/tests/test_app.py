from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_docs():
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
