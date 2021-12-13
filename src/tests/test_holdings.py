from uuid import uuid4
from ..holdings.holdings import Holdings
from datetime import date
from decimal import Decimal


class TestHoldings:
    """
    Tests for holdings class
    """

    def test_is_empty(self):
        """Tests for holdings is_mepty method"""
        holdings = Holdings()
        assert holdings.is_empty()
        holdings.add_holding(uuid4(), date(2022, 2, 2), Decimal(123))
        assert not holdings.is_empty()

    def test_get_security_ids(self):
        """Tests for holdings get_security_ids method"""
        holdings = Holdings()

        assert [] == holdings.get_security_ids()

        security_1_id = uuid4()
        security_2_id = uuid4()
        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 2, 2), amount=Decimal(123))
        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 2, 2), amount=Decimal(123))
        holdings.add_holding(security_id=security_2_id, holding_date=date(2022, 2, 2), amount=Decimal(123))
        assert 2 == len(holdings.get_security_ids())
        assert [security_1_id, security_2_id] == holdings.get_security_ids()

    def test_get_security_dates(self):
        """Tests for holdings get_security_dates method"""
        security_1_id = uuid4()
        security_2_id = uuid4()

        holdings = Holdings()
        assert holdings.get_security_min_date(security_id=security_1_id) is None
        assert holdings.get_security_max_date(security_id=security_1_id) is None
        assert holdings.get_security_min_date(security_id=security_2_id) is None
        assert holdings.get_security_max_date(security_id=security_2_id) is None

        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 2, 2), amount=Decimal(123))
        assert date(2022, 2, 2) == holdings.get_security_min_date(security_id=security_1_id)
        assert date(2022, 2, 2) == holdings.get_security_max_date(security_id=security_1_id)
        assert holdings.get_security_min_date(security_id=security_2_id) is None
        assert holdings.get_security_max_date(security_id=security_2_id) is None

        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 2, 1), amount=Decimal(123))
        assert date(2022, 2, 1) == holdings.get_security_min_date(security_id=security_1_id)
        assert date(2022, 2, 2) == holdings.get_security_max_date(security_id=security_1_id)
        assert holdings.get_security_min_date(security_id=security_2_id) is None
        assert holdings.get_security_max_date(security_id=security_2_id) is None

        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 2, 3), amount=Decimal(123))
        assert date(2022, 2, 1) == holdings.get_security_min_date(security_id=security_1_id)
        assert date(2022, 2, 3) == holdings.get_security_max_date(security_id=security_1_id)
        assert holdings.get_security_min_date(security_id=security_2_id) is None
        assert holdings.get_security_max_date(security_id=security_2_id) is None

        holdings.add_holding(security_id=security_2_id, holding_date=date(2022, 1, 1), amount=Decimal(123))
        assert date(2022, 2, 1) == holdings.get_security_min_date(security_id=security_1_id)
        assert date(2022, 2, 3) == holdings.get_security_max_date(security_id=security_1_id)
        assert date(2022, 1, 1) == holdings.get_security_min_date(security_id=security_2_id)
        assert date(2022, 1, 1) == holdings.get_security_max_date(security_id=security_2_id)

    def test_get_day_sum(self):
        """Tests for holdings get_day_sum method"""
        security_1_id = uuid4()
        security_2_id = uuid4()

        holdings = Holdings()

        assert Decimal(0) == holdings.get_day_sum(holding_date=date(2022, 1, 1), currency_rates={}, security_rates={})

        holdings.add_holding(security_id=security_1_id, holding_date=date(2022, 1, 1), amount=Decimal(100))
        holdings.add_holding(security_id=security_2_id, holding_date=date(2022, 1, 1), amount=Decimal(1000))

        assert Decimal(1100) == holdings.get_day_sum(holding_date=date(2022, 1, 1),
                                                     security_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(1)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     },
                                                     currency_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(1)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     })

        assert Decimal(1200) == holdings.get_day_sum(holding_date=date(2022, 1, 1),
                                                     security_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(2)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     },
                                                     currency_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(1)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     })

        assert Decimal(1050) == holdings.get_day_sum(holding_date=date(2022, 1, 1),
                                                     security_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(1)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     },
                                                     currency_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(2)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(1)}
                                                     })

        assert Decimal(1100) == holdings.get_day_sum(holding_date=date(2022, 1, 1),
                                                     security_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(2)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(2)}
                                                     },
                                                     currency_rates={
                                                         security_1_id: {date(2022, 1, 1): Decimal(2)},
                                                         security_2_id: {date(2022, 1, 1): Decimal(2)}
                                                     })
