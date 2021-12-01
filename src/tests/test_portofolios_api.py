import datetime

from sqlalchemy import create_engine
import factory.fuzzy
from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.mysql import *  # noqa
from .fixtures.sql_factories import *
from sqlalchemy.orm import scoped_session, sessionmaker
from factory.faker import faker

from ..utils.uuid_utils import uuid_to_short_form

logger = logging.getLogger(__name__)

faker = faker.Faker()


class TestPortofolios:
    def setup(self):
        """
        prepare default values for test case
        """
        self.session = None
        self.engine = None
        self.SO_SEC_NR = "010170-999R"
        self.NAME1 = "ExampleFirstName ExampleLastName"
        self.other_ssn = faker.ssn()
        self.other_name = faker.name()
        self.currency = ["EUR", "SEK", "other"]
        self.sec_sec_ids = ["Non Euro Fund", "test fund 1", "test fund 2", "test fund 3", "test fund 4"]
        self.sec_corr = [4.0000, 4.0000, 4.0000, 4.0000, 4.0000]
        self.sec_curr = ["SEK", "EUR", "EUR", "EUR", "EUR"]
        self.com_code = 10032
        self.other_com_code = 230230
        base = datetime.datetime.today()

        self.amounts = [76.842500, 76.842500, 76.842500, 443.360600, 431.719200, 431.108800, 428.170100,
                        0.581600, 167.063500, 167.012100, 166.914500, 445.467100, 0.854900, 761.347800, 768.887700,
                        769.905900, 755.321200, 94.893700, 410.866500, 410.866500, 95.418300, 94.620600, 384.955900,
                        85.503900, 1229.477000, 174.392800]

        self.PUR_CVALUE = [5000.00, 5000.00, 5000.00, 5000.00,
                           5000.00, 5000.00, 5000.00, 41.47, 5000.00, 5000.00, 5000.00, 14908.97, 68.69, 5000.00,
                           5000.00, 5000.00,
                           5000.00, 5000.00, 5000.00, 5000.00, 5000.00, 5000.00, 5000.00, 5000.00, 10099.17, 10147.38]

        self.sec_ids = ["Non Euro Fund", "Non Euro Fund", "Non Euro Fund", "test fund 1", "test fund 1", "test fund 1",
                        "test fund 1", "test fund 2", "test fund 3", "test fund 3", "test fund 3", "test fund 3",
                        "test fund 2", "test fund 1", "test fund 1",
                        "test fund 1", "test fund 1", "test fund 2", "test fund 4", "test fund 4", "test fund 2",
                        "test fund 2", "test fund 4",
                        "test fund 2", "test fund 1", "test fund 2"]

        self.rates = [
            ("test fund 1", 14.116300), ("test fund 4", 12.274700),
            ("test fund 2", 88.046300), ("SEK", 9.971300),
            ("Non Euro Fund", 1313.410000), ("test fund 3", 39.209700)]

        self.porid = "03568d76-93f1-3a2d-9ed5-b95516546548"
        self.other_por_id = "03568d76-93f1-3a2d-9ed5-b95516546549"

        self.expected_results = {
            "test fund 1": ("test fund 1", 6019.298300, 50099.17, 84970.2205922900000000),
            "test fund 2": ("test fund 2", 546.265800, 30257.54, 48096.6825065400000000),
            "test fund 3": ("test fund 3", 946.457200, 29908.97, 37110.3028748400000000),
            "test fund 4": ("test fund 4", 1206.688900, 15000.00, 14811.7442408300000000),
            "Non Euro Fund": ("Non Euro Fund", 230.527500, 15000.00, 30364.8595243348409937)
        }
        self.expected_total_amounts = [6019.298300, 546.265800, 946.457200, 1206.688900, 230.527500]
        self.expected_purchase_totals = [50099.17, 30257.54, 29908.97, 15000.00, 15000.00]
        self.expected_market_value_totals = [84970.2205922900000000, 48096.6825065400000000, 37110.3028748400000000,
                                             14811.7442408300000000, 30364.8595243348409937]
        self.expected_sum_total_amount = int(
            sum([(total_amount * 100) for total_amount in self.expected_total_amounts]))
        self.expected_sum_purchase_total = int(
            sum([(purchase_total * 100) for purchase_total in self.expected_purchase_totals]))
        self.expected_sum_market_value_total = int(
            sum([(market_value_total * 100) for market_value_total in self.expected_market_value_totals]))

        self.first_index = faker.pyint(min_value=0, max_value=19)
        self.last_index = faker.pyint(min_value=20, max_value=39)
        self.date_list = [(base - datetime.timedelta(days=x)).date() for x in range(40)]
        self.transaction_code = ["11" if x < 20 else "12" for x in range(40)]
        self.ctot_values = [faker.pydecimal(left_digits=13, right_digits=2, positive=True) for _ in range(40)]
        self.start_date = self.date_list[self.last_index].isoformat()
        self.end_date = self.date_list[self.first_index].isoformat()

        self.expected_subscription = sum(self.ctot_values[self.first_index:20])
        self.expected_redemption = sum(self.ctot_values[20:self.last_index])

    def set_session(self, mysql: MySqlContainer):
        """
        prepare database session
        """
        self.engine = create_engine(mysql.get_connection_url())
        self.session = scoped_session(sessionmaker(bind=self.engine))
        for cls_factory in factory.alchemy.SQLAlchemyModelFactory.__subclasses__():
            cls_factory._meta.sqlalchemy_session = self.session

    def prepare_test_suit(self):
        """
        insert the test data into database
        """
        COMPANYrahFactory(COM_CODE=self.com_code,
                          SO_SEC_NR=self.SO_SEC_NR,
                          NAME1=self.NAME1)

        for idx, sec in enumerate(self.sec_sec_ids):
            SECURITYrahFactory(
                SECID=self.sec_sec_ids[idx],
                NAME1=factory.fuzzy.FuzzyText(length=255),
                CURRENCY=self.sec_curr[idx],
                PE_CORR=self.sec_corr[idx]
            )

        for rate in self.rates:
            RATELASTrahFactory(SECID=rate[0],
                               RCLOSE=rate[1]
                               )

        for idx, x in enumerate(self.sec_ids):
            PORTRANSrahFactory(
                COM_CODE=self.com_code,
                PORID=uuid_to_short_form(self.porid),
                SECID=self.sec_ids[idx],
                AMOUNT=self.amounts[idx],
                PUR_CVALUE=self.PUR_CVALUE[idx]
            )

        PORTFOLrahFactory(PORID=uuid_to_short_form(self.porid),
                          COM_CODE=self.com_code,
                          NAME1=self.NAME1)

        PORTFOLrahFactory(PORID=uuid_to_short_form(self.other_por_id),
                          COM_CODE=self.other_com_code)

        for idx, transaction_date in enumerate(self.date_list):
            PORTLOGrahFactory(TRANS_CODE=self.transaction_code[idx],
                              TRANS_DATE=transaction_date,
                              CTOT_VALUE=self.ctot_values[idx],
                              PORID=uuid_to_short_form(self.porid)
                              )
        self.session.commit()

    def test_find_portfolio(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to find portfolio from portfolio id
        """
        self.set_session(mysql)
        self.prepare_test_suit()

        response = client.get(f"/v1/portfolios/{self.porid}", auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 4 == len(values)
        assert uuid_to_short_form(self.porid) == values["id"]
        assert self.expected_sum_total_amount == values["totalAmount"]
        assert self.expected_sum_market_value_total == values["marketValueTotal"]
        assert self.expected_sum_purchase_total == values["purchaseTotal"]

    def test_get_portfolio_h_summary(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to find portfolio history from portfolio id in a given period
        """
        response = client.get(
            f"/v1/portfolios/{self.porid}/summary?startDate={self.start_date}&endDate={self.end_date}",
            auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 2 == len(values)

    def test_portfolio_history_values(self):
        pass  # todo development after new database changes

    def test_list_portfolios(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to list portfolios of a user
        """
        response = client.get("/v1/portfolios/", auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 1 == len(values)
        assert self.expected_sum_total_amount == values[0]["totalAmount"]
        assert self.expected_sum_market_value_total == values[0]["marketValueTotal"]
        assert self.expected_sum_purchase_total == values[0]["purchaseTotal"]
