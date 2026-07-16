import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_providers(client):
    res = client.get("/providers")
    assert res.status_code == 200
    data = res.json()
    assert "active" in data
    assert "available" in data
    assert "mock" in data["available"]


def test_tracks(client):
    res = client.get("/tracks")
    assert res.status_code == 200
    data = res.json()
    assert "tracks" in data
    assert "direct" in data["tracks"]


def test_config(client):
    res = client.get("/config")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "tracks" in data
    assert "providers" in data


def test_chat_empty_prompt(client):
    res = client.post("/chat", json={"prompt": ""})
    assert res.status_code == 400


def test_chat_mock(client):
    res = client.post("/chat", json={"prompt": "test prompt", "provider": "mock"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "validation" in data
    assert "timing" in data
    assert "MOCK_ANSWER" in data["answer"]


def test_chat_default_provider(client):
    res = client.post("/chat", json={"prompt": "hello"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data


def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
