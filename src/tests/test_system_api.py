from starlette.testclient import TestClient

from .fixtures.client import *  # noqa

class TestSystem:
    """Tests for system endpoints"""

    def test_ping(self, client: TestClient):
        response = client.get("/v1/system/ping")
        assert response.status_code == 200
        assert response.json() == "pong"
