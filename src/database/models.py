from uuid import uuid4

from .sqlalchemy_uuid import SqlAlchemyUuid
from sqlalchemy import Column, DECIMAL, Integer, String, ForeignKey, Date, CHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Fund(Base):
    __tablename__ = 'fund'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    fund_id = Column(Integer, index=True, unique=True)
    security_id = Column(String(24), index=True, unique=True)
    security_name_fi = Column(String(191), nullable=False)
    security_name_sv = Column(String(191), nullable=False)
    rates = relationship("FundRate", back_populates="fund", lazy=True)


class FundRate(Base):
    __tablename__ = 'fund_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    fund_id = Column("fund_id", SqlAlchemyUuid, ForeignKey('fund.id'))
    rate_date = Column("rate_date", Date)
    rate_close = Column(DECIMAL(19, 6), nullable=False)
    fund = relationship("Fund", back_populates="rates", lazy=True)


class Company(Base):
    __tablename__ = 'company'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    company_code = Column(String(20), index=True, unique=True)
    ssn = Column(String(11))


class Security(Base):
    __tablename__ = 'security'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column(String(20), index=True, primary_key=True)
    currency = Column(CHAR(3))
    pe_corr = Column(DECIMAL(8, 4))
    isin = Column(String(12))


class LastRate(Base):
    __tablename__ = 'last_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column(String(20), index=True, unique=True)
    rate_close = Column(DECIMAL(16, 6))


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    # portfolio_id is either equal to company_code or it has a format like c_n where c is company_code value
    # and n is a number with maximum value of 8
    portfolio_id = Column(String(20), unique=True)
    company_code = Column(String(20), index=True)


class PortfolioLog(Base):
    __tablename__ = 'portfolio_log'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    transaction_number = Column(Integer, index=True, unique=True)
    transaction_code = Column(CHAR(2), index=True)
    transaction_date = Column(DateTime, index=True)
    company_code = Column(String(20), index=True)
    portfolio_id = Column(String(20), index=True)
    c_total_value = Column(DECIMAL(15, 2))


class PortfolioTransaction(Base):
    __tablename__ = 'portfolio_transaction'
    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    transaction_number = Column(Integer, unique=True)
    company_code = Column(String(20), index=True)

    portfolio_id = Column(String(20), index=True)
    security_id = Column(String(20), index=True)
    transaction_date = Column(DateTime)
    amount = Column(DECIMAL(19, 6))
    purchase_c_value = Column(DECIMAL(15, 2))
