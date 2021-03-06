from uuid import uuid4

from .sqlalchemy_uuid import SqlAlchemyUuid
from sqlalchemy import Index, Column, DECIMAL, Integer, String, ForeignKey, Date, CHAR, DateTime, SmallInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Fund(Base):
    __tablename__ = 'fund'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(Integer, index=True, unique=True)
    risk_level = Column(Integer, nullable=True)
    group = Column(name="fund_group", type_=String(191), nullable=True)
    kiid_url_fi = Column(String(191), nullable=True)
    kiid_url_sv = Column(String(191), nullable=True)
    kiid_url_en = Column(String(191), nullable=True)
    deprecated = Column(Boolean, nullable=False)
    # a fund contains one or more securities
    securities = relationship("Security", back_populates="fund", lazy=True)


class Security(Base):
    __tablename__ = 'security'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(20), index=True, unique=True, nullable=False)
    currency = Column(CHAR(3))
    name_fi = Column(String(191), nullable=False)
    name_sv = Column(String(191), nullable=False)
    name_en = Column(String(191), nullable=False)
    series_id = Column(SmallInteger, nullable=True)
    rates = relationship("SecurityRate", back_populates="security", lazy=True)
    last_rate = relationship("LastRate", back_populates="security", lazy=True)
    fund = relationship("Fund", back_populates="securities", lazy=True)
    fund_id = Column("fund_id", SqlAlchemyUuid, ForeignKey('fund.id'), nullable=True)
    portfolio_transactions = relationship("PortfolioTransaction", back_populates="security", lazy=True)
    c_portfolio_logs = relationship("PortfolioLog", back_populates="c_security", lazy=True,
                                    foreign_keys="PortfolioLog.c_security_id")
    portfolio_logs = relationship("PortfolioLog", back_populates="security", lazy=True,
                                  foreign_keys="PortfolioLog.security_id")
    updated = Column(DateTime, index=True, server_default="1970-01-01")


class SecurityRate(Base):
    __tablename__ = 'security_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), nullable=False)
    security = relationship("Security", back_populates="rates", lazy=True)
    rate_date = Column("rate_date", Date)
    rate_close = Column(DECIMAL(19, 6), nullable=False)
    __table_args__ = (Index("ix_security_rate_security_id_rate_date", "security_id", "rate_date", unique=True),)


class Company(Base):
    __tablename__ = 'company'

    # A user can have multiple portfolios with the same company code, company code represents the user.
    # original id = company_code
    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(20), index=True, unique=True)
    ssn = Column(String(11))
    name = Column(String(192), nullable=False)
    updated = Column(DateTime, nullable=False)
    portfolios = relationship("Portfolio", back_populates="company", lazy=True)
    company_access = relationship("CompanyAccess", back_populates="company", lazy=True)
    c_portfolio_logs = relationship("PortfolioLog", back_populates="c_company", lazy=True,
                                    foreign_keys="PortfolioLog.c_company_id")


class CompanyAccess(Base):
    __tablename__ = 'company_access'
    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    ssn = Column(String(11), nullable=False)
    company_id = Column("company_id", SqlAlchemyUuid, ForeignKey('company.id'), index=True, nullable=False)
    company = relationship("Company", back_populates="company_access", lazy=True)


class LastRate(Base):
    __tablename__ = 'last_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), nullable=False)
    security = relationship("Security", back_populates="last_rate", lazy=True)
    rate_date = Column(Date, nullable=False)
    rate_close = Column(DECIMAL(16, 6))
    __table_args__ = (Index("ix_last_rate_security_id_rate_date", "security_id", "rate_date"),)


class Portfolio(Base):
    __tablename__ = 'portfolio'
    # original_id is either equal to company_code or it has a format like c_n where c is company_code value
    # and n is a number with maximum value of 8

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    name = Column(String(192), nullable=False)
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
    security_id = Column("security_id", SqlAlchemyUuid, ForeignKey('security.id'), index=True, nullable=False)
    c_security_id = Column("c_security_id", SqlAlchemyUuid, ForeignKey('security.id'), index=True, nullable=True)
    c_company_id = Column("c_company_id", SqlAlchemyUuid, ForeignKey('company.id'), index=True, nullable=True)

    amount = Column(DECIMAL(19, 6), nullable=False)
    c_price = Column(DECIMAL(19, 6), nullable=False)
    payment_date = Column(Date, index=True, nullable=True)
    c_value = Column(DECIMAL(15, 2), nullable=False)
    provision = Column(DECIMAL(15, 2), nullable=False)
    status = Column(CHAR(1), nullable=False)
    updated = Column(DateTime, nullable=False)

    portfolio = relationship("Portfolio", back_populates="portfolio_logs", lazy=True)
    c_security = relationship("Security", back_populates="c_portfolio_logs", lazy=True,
                              foreign_keys="PortfolioLog.c_security_id")
    security = relationship("Security", back_populates="portfolio_logs", lazy=True,
                            foreign_keys="PortfolioLog.security_id")
    c_company = relationship("Company", back_populates="c_portfolio_logs", lazy=True,
                             foreign_keys="PortfolioLog.c_company_id")
    __table_args__ = (Index("ix_portfolio_log_security_id_updated", "security_id", "updated"),)


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
    updated = Column(DateTime, nullable=False)
    __table_args__ = (Index("ix_portfolio_transaction_security_id_updated", "security_id", "updated"),)


class SynchronizationFailure(Base):
    __tablename__ = 'synchronization_failure'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    original_id = Column(String(191), nullable=False)
    message = Column(String(191), nullable=False)
    origin_task = Column(String(191), nullable=False)
    target_task = Column(String(191), nullable=False)
    action = Column(Integer, nullable=False)
    handled = Column(Boolean, nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
