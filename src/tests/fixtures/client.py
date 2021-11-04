import pytest
from starlette.testclient import TestClient
from ...app.main import app


@pytest.fixture()
def client():
    """Fixture for test REST client

    Returns:
        TestClient: test REST client
    """
    return TestClient(app)
