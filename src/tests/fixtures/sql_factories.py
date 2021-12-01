from factory.faker import faker
import factory.fuzzy
import random

from src.database.sqlalchemy_models import SECURITYrah, COMPANYrah, PORTFOLrah, PORTRANSrah, RATELASTrah, PORTLOGrah

faker = faker.Faker()


class COMPANYrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = COMPANYrah

    COM_CODE = faker.unique.pyint(),
    SO_SEC_NR = faker.ssn()
    NAME1 = faker.name()


class PORTRANSrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PORTRANSrah

    TRANS_NR = factory.Sequence(lambda n: n)
    COM_CODE = faker.pyint()
    PORID = faker.pyint()
    SECID = factory.fuzzy.FuzzyText(length=20)
    TRANS_DATE = faker.date_time()
    AMOUNT = factory.fuzzy.FuzzyDecimal(low=0, high=9999999999999999999, precision=6)
    PUR_CVALUE = factory.fuzzy.FuzzyDecimal(low=0, high=999999999999999, precision=2)


class PORTFOLrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PORTFOLrah

    PORID = factory.Sequence(lambda n: n)
    COM_CODE = faker.pyint(),
    NAME1 = faker.name(),
    POR_TYPE = random.choice(["10", "90"]),


class SECURITYrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SECURITYrah

    SECID = factory.fuzzy.FuzzyText(length=20)
    NAME1 = factory.fuzzy.FuzzyText(length=255)
    CURRENCY = faker.currency()
    PE_CORR = faker.pydecimal(left_digits=4, right_digits=4, positive=True)
    ISIN = factory.fuzzy.FuzzyText(length=12)


class RATELASTrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RATELASTrah

    SECID = factory.fuzzy.FuzzyText(length=20)
    RDATE = faker.date_time()
    RCLOSE = factory.fuzzy.FuzzyDecimal(low=0, high=9999999999999999, precision=6)


class PORTLOGrahFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PORTLOGrah

    TRANS_NR = factory.Sequence(lambda n: n)
    TRANS_CODE = factory.fuzzy.FuzzyText(length=2)
    TRANS_DATE = faker.date_time()
    COM_CODE = faker.pyint(),
    CTOT_VALUE = faker.pydecimal(left_digits=13, right_digits=2, positive=True)
