import pytest
import os

from starlette.testclient import TestClient
from ...app.main import app

data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
funds_json = os.path.join(data_folder, 'funds.json')
fund_options_json = os.path.join(data_folder, 'fund-options.json')
fund_values_csv = os.path.join(data_folder, 'fund-values.csv')


@pytest.fixture()
def client() -> TestClient:
    """Fixture for test REST client

    Returns:
        TestClient: test REST client
    """

    os.environ["FUND_JSON"] = funds_json
    os.environ["FUND_OPTIONS_JSON"] = fund_options_json
    os.environ["FUND_VALUES_CSV"] = fund_values_csv

    return TestClient(app)
