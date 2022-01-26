from ..utils.portfolio_utils import PortfolioUtils
from .fixtures.client import *  # noqa
from .fixtures.backend_mysql import *  # noqa


class TestPortfolioUtils:
    """Tests for system endpoints"""
    def test_get_portfolio_key(self, client: TestClient):
        key = "123456"
        result = PortfolioUtils.get_portfolio_key(key)
        assert result == "0001"
        key = "1234567_2"
        result = PortfolioUtils.get_portfolio_key(key)
        assert result == "0201"

    def test_make_reference(self, client:TestClient):
        share = "10"
        port = "0401"
        com = "12345"
        result = PortfolioUtils.make_reference(share,com,port)
        assert result == "101234504019"
        share = "20"
        port = "0401"
        com = "67890"
        result = PortfolioUtils.make_reference(share,com,port)
        assert result == "206789004011"

        share = "10"
        port = "0501"
        com = "67890"
        result = PortfolioUtils.make_reference(share, com, port)
        assert result == "106789005013"
