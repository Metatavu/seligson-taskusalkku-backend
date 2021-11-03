from starlette.testclient import TestClient

from ..app.main import app

client = TestClient(app)


def test_ping():
    response = client.get("/v1/system/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
