from starlette.testclient import TestClient

from ..app.main import app

client = TestClient(app)


def test_find_fund():
    response = client.get("/v1/funds/D44C5F1E-F41B-45D6-B7A6-EF6BF7873E59")
    assert response.status_code == 200
    # TODO: Add actual tests
