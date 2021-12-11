from uuid import uuid4

from .sqlalchemy_uuid import SqlAlchemyUuid
from sqlalchemy import Column, DECIMAL, Integer, String, ForeignKey, Date, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Fund(Base):
    __tablename__ = 'fund'

    # a fund contains one or more securities
    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(Integer, index=True, unique=True)
    securities = relationship("Security", back_populates="fund", lazy=True)


class Security(Base):
    __tablename__ = 'security'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(20), index=True, unique=True, nullable=False)
    currency = Column(CHAR(3))
    name_fi = Column(String(191), nullable=False)
    name_sv = Column(String(191), nullable=False)
    rates = relationship("SecurityRate", back_populates="security", lazy=True)
    last_rate = relationship("LastRate", back_populates="security", lazy=True)
    fund = relationship("Fund", back_populates="securities", lazy=True)
    fund_id = Column("fund_id", SqlAlchemyUuid, ForeignKey('fund.id'), nullable=True)
    portfolio_transactions = relationship("PortfolioTransaction", back_populates="security", lazy=True)


class SecurityRate(Base):
    __tablename__ = 'security_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), nullable=False)
    security = relationship("Security", back_populates="rates", lazy=True)
    rate_date = Column("rate_date", Date)
    rate_close = Column(DECIMAL(19, 6), nullable=False)


class Company(Base):
    __tablename__ = 'company'

    # A user can have multiple portfolios with the same company code, company code represents the user.
    # original id = company_code
    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(20), index=True, unique=True)
    ssn = Column(String(11))
    portfolios = relationship("Portfolio", back_populates="company", lazy=True)


class LastRate(Base):
    __tablename__ = 'last_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), nullable=False)
    security = relationship("Security", back_populates="last_rate", lazy=True)
    rate_close = Column(DECIMAL(16, 6))


class Portfolio(Base):
    __tablename__ = 'portfolio'
    # original_id is either equal to company_code or it has a format like c_n where c is company_code value
    # and n is a number with maximum value of 8

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(20), unique=True, nullable=False)
    company_id = Column("company_id", SqlAlchemyUuid, ForeignKey('company.id'), index=True, nullable=False)
    company = relationship("Company", back_populates="portfolios", lazy=True)
    portfolio_logs = relationship("PortfolioLog", back_populates="portfolio", lazy=True)
    portfolio_transactions = relationship("PortfolioTransaction", back_populates="portfolio", lazy=True)


class PortfolioLog(Base):
    __tablename__ = 'portfolio_log'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    transaction_number = Column(Integer, index=True, unique=True)
    transaction_code = Column(CHAR(2), index=True)
    transaction_date = Column(Date, index=True)
    c_total_value = Column(DECIMAL(15, 2))
    portfolio_id = Column("portfolio_id", SqlAlchemyUuid, ForeignKey('portfolio.id'), index=True, nullable=False)
    portfolio = relationship("Portfolio", back_populates="portfolio_log", lazy=True)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), index=True, nullable=False)
    security = relationship("Security", back_populates="portfolio_log", lazy=True)
    c_security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), index=True, nullable=True)
    c_security = relationship("Security", back_populates="portfolio_log", lazy=True)
    amount = Column(DECIMAL(19, 6), nullable=False)
    c_price = Column(DECIMAL(19, 6), nullable=False)
    payment_date = Column(Date, index=True, nullable=False)
    c_value = Column(DECIMAL(15, 2), nullable=False)
    provision = Column(DECIMAL(15, 2), nullable=True)
    status = Column(CHAR(1), nullable=False)

class PortfolioTransaction(Base):
    __tablename__ = 'portfolio_transaction'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    transaction_number = Column(Integer, unique=True)
    transaction_date = Column(Date)
    amount = Column(DECIMAL(19, 6))
    purchase_c_value = Column(DECIMAL(15, 2))
    portfolio_id = Column("portfolio_id", SqlAlchemyUuid, ForeignKey('portfolio.id'), index=True, nullable=False)
    portfolio = relationship("Portfolio", back_populates="portfolio_transactions", lazy=True)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), index=True, nullable=False)
    security = relationship("Security", back_populates="portfolio_transactions", lazy=True)