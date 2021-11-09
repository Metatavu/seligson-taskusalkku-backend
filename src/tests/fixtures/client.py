import pytest
import os

from starlette.testclient import TestClient
from ...app.main import app

funds_meta_json = os.path.join(os.path.dirname(__file__),
                                    '..',
                                    'data',
                                    'funds-meta.json')

@pytest.fixture()
def client() -> TestClient:
    """Fixture for test REST client

    Returns:
        TestClient: test REST client
    """

    os.environ["FUND_META_JSON"] = funds_meta_json
    
    return TestClient(app)
