from decimal import Decimal
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import coalesce

from .models import Fund, SecurityRate, Company, CompanyAccess, PortfolioTransaction, LastRate, Security, Portfolio, \
    PortfolioLog
from datetime import date


def find_fund(database: Session, fund_id: UUID) -> Optional[Fund]:
    """Queries the fund table

        Args:
            database (Session): database session
            fund_id (UUID): fund id

        Returns:
            Optional[Fund]: matching Fund row or none
        """
    return database.query(Fund) \
        .filter(Fund.id == fund_id) \
        .one_or_none()


def list_funds(database: Session,
               deprecated: bool,
               first_result: int,
               max_result: int
               ) -> List[Fund]:
    """Queries the fund table

    Args:
        database (Session): database session
        deprecated: filter by deprecated
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[Fund]: list of all Fund table rows
    """
    return database.query(Fund) \
        .filter(Fund.deprecated == deprecated)\
        .order_by(Fund.original_id) \
        .offset(first_result) \
        .limit(max_result) \
        .all()


def find_security(database: Session, security_id: UUID) -> Optional[Security]:
    """Queries the fund table

        Args:
            database (Session): database session
            security_id (UUID): security id

        Returns:
            Optional[Security]: matching security row or none
        """
    return database.query(Security) \
        .filter(Security.id == security_id) \
        .one_or_none()


def find_main_security_for_fund(database: Session, fund_id: UUID) -> Optional[Security]:
    """
    Finds 'main' security for a fund. Main security is a security with the lowest series id.

    Args:
        database (Session): database session
        fund_id (UUID): fund id

    Returns:
            Optional[Security]: found security or none if not found
    """
    return database.query(Security)\
        .filter(Security.fund_id == fund_id)\
        .order_by(coalesce(Security.series_id, 99))\
        .limit(1)\
        .one_or_none()


def list_securities_with_fund(database: Session,
                              first_result: int,
                              max_result: int,
                              series_id: Optional[int] = None,
                              fund_id: Optional[UUID] = None
                              ) -> List[Security]:
    """Lists securities with not null fund

    Args:
        database (Session): database session
        first_result (int): first result. Defaults to 0.
        max_result (int): max results. Defaults to 100.
        series_id(int, optional): the class type of the security 1,2 or None.
        fund_id(UUID, optional): fund id.

    Returns:
        List[Security]: list of security with fund_id
    """
    query = database.query(Security)
    if fund_id:
        query = query.filter(Security.fund_id == fund_id)
    if series_id:
        query = query.filter(Security.series_id == series_id)
    # if no series id then return all of them despite the class
    return query.filter(Security.fund_id.is_not(None)) \
        .order_by(Security.original_id) \
        .offset(first_result) \
        .limit(max_result) \
        .all()


def get_last_rate_date_for_security_rate(database: Session, security_id: UUID) -> date:
    """
    Returns the last rate date for a security.

    Args:
        database (Session): database session
        security_id (UUID): security id

    Returns:
        Optional[datetime]: last rate date
    """
    return database.query(func.max(SecurityRate.rate_date)) \
        .filter(SecurityRate.security_id == security_id) \
        .scalar()


def query_security_rates(database: Session,
                         security_id: UUID,
                         rate_date_min: date,
                         rate_date_max: date,
                         first_result: Optional[int] = None,
                         max_result: Optional[int] = None
                         ) -> List[SecurityRate]:
    """Queries the security rates

    Args:
        database (Session): database session
        security_id (UUID): security id
        rate_date_min (date): filter results by rate_date after given date
        rate_date_max (date): filter results by rate_date before given date
        first_result (int, optional): first result
        max_result (int, optional): max results

    Returns:
        List[SecurityRate]: list of matching SecurityRate table rows
    """

    query = database.query(SecurityRate) \
        .filter(SecurityRate.rate_date >= rate_date_min) \
        .filter(SecurityRate.rate_date <= rate_date_max) \
        .filter(SecurityRate.security_id == security_id)

    if first_result:
        query = query.offset(first_result)

    if max_result:
        query = query.limit(max_result)

    return query.all()


def find_most_recent_security_rate(database: Session,
                                   security_id: UUID,
                                   rate_date_before: date
                                   ) -> Optional[SecurityRate]:
    """Find most recent security rate before given time

    Args:
        database (Session): database session
        security_id (UUID): security id
        rate_date_before (date): date before (or at same day) the returned rate should be

    Returns:
        Optional[SecurityRate]: SecurityRate or None if not found
    """

    return database.query(SecurityRate) \
        .filter(SecurityRate.security_id == security_id) \
        .filter(SecurityRate.rate_date <= rate_date_before) \
        .order_by(SecurityRate.rate_date.desc()) \
        .limit(1) \
        .one_or_none()


def find_company(database: Session, company_id: UUID) -> Optional[Company]:
    """Queries the company table

    Args:
        database (Session): database session
        company_id (UUID): company id
    Returns:
        List[Company]: list of matching company table rows
    """

    return database.query(Company).filter(Company.id == company_id).one_or_none()


def get_companies(database: Session, ssn: str) -> List[Company]:
    """Queries the company table

    Args:
        database (Session): database session
        ssn (str): ssn of user/ or company id
    Returns:
        List[Company]: list of matching company table rows
    """

    return database.query(Company).filter(Company.ssn == ssn)\
        .order_by(Company.name).all()


def get_company_access(database: Session, ssn: str) -> List[CompanyAccess]:
    """Queries the company access table

    Args:
        database (Session): database session
        ssn (str): ssn of user/ or company id
    Returns:
        List[CompanyAccess]: list of matching company access table rows
    """

    return database.query(CompanyAccess).filter(CompanyAccess.ssn == ssn).all()


def find_company_access_by_ssn_and_company_id(database: Session, ssn: str, company_id: UUID) -> Optional[CompanyAccess]:
    """Finds company access row by ssn and company_id

    Args:
        database (Session): database session
        ssn (str): ssn of user
        company_id (UUID): company id
    Returns:
        Optional[CompanyAccess]: found company access or None if not found
    """

    return database.query(CompanyAccess)\
        .filter(CompanyAccess.ssn == ssn) \
        .filter(CompanyAccess.company_id == company_id) \
        .one_or_none()


def find_portfolio(database: Session, portfolio_id: UUID) -> Optional[Portfolio]:
    """Finds portfolio from the database

    Args:
            database (Session): database session
            portfolio_id (UUID): portfolio id
    """
    return database.query(Portfolio) \
        .filter(Portfolio.id == portfolio_id) \
        .one_or_none()


def get_portfolio_summary(database: Session, portfolio: Portfolio, start_date: date, end_date: date,
                          transaction_codes: [str]) -> List[PortfolioLog]:
    """Queries the portfolio_log table

        Args:
            database (Session): database session
            transaction_codes ([str]): list of valid transaction_code for the operation
            start_date (date): filter results from this date
            end_date (date): filter results to this date
            portfolio (Portfolio): portfolio
        Returns:
             List[PortfolioLog]: rows of portfolio_log
        """

    return database.query(PortfolioLog)\
        .filter(PortfolioLog.transaction_code.in_(transaction_codes))\
        .filter(PortfolioLog.status == '0')\
        .filter(PortfolioLog.transaction_date >= start_date.isoformat())\
        .filter(PortfolioLog.transaction_date <= end_date.isoformat())\
        .filter(PortfolioLog.portfolio == portfolio)\
        .all()


def get_portfolio_security_values(database: Session, portfolio: Portfolio) -> List:
    """ Queries for portfolio securities

        Args:
            database (Session): database session
            portfolio (Portfolio): portfolio
        Returns:
             List[PortfolioSecurityValues]: list of portfolio securities
    """
    return database.query(Portfolio,
                          Security.currency.label("currency"),
                          PortfolioTransaction.security_id.label("security_id"),
                          func.sum(PortfolioTransaction.amount).label("total_amount"),
                          func.sum(PortfolioTransaction.purchase_c_value).label("purchase_total"),
                          func.sum(LastRate.rate_close * PortfolioTransaction.amount).label("market_value_total")
                          ) \
        .join(PortfolioTransaction, Portfolio.id == PortfolioTransaction.portfolio_id) \
        .join(LastRate, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.id) \
        .filter(Portfolio.id == portfolio.id) \
        .group_by(Security.id)\
        .all()


def get_currency_rate_map(database: Session, currencies: List[str]) -> Dict[str, Decimal]:
    """
    Returns conversion map from currency to EUR
    Args:
        database: database session
        currencies: currencies to be returned

    Returns: conversion map from currency to EUR
    """
    rows = database.query(Security.original_id.label("currency"), LastRate.rate_close.label("rate_close"))\
        .join(Security, LastRate.security_id == Security.id)\
        .filter(Security.original_id.in_(currencies))\
        .all()

    result = {}

    for row in rows:
        result[row.currency] = row.rate_close

    return result


def get_portfolio_logs(database: Session,
                       portfolio: Portfolio,
                       transaction_codes: List[str],
                       transaction_date_min: Optional[date],
                       transaction_date_max: Optional[date],
                       first_result: Optional[int] = None,
                       max_result: Optional[int] = None
                       ) -> List[PortfolioLog]:
    """ Queries for portfolio logs

        Args:
            database (Session): database session
            portfolio (Portfolio): portfolio
            transaction_codes (List[str]): filter by transaction codes
            transaction_date_min (date): filter results by transaction_date after given date
            transaction_date_max (date): filter results by transaction_date before given date
            first_result (int, optional): first result.
            max_result (int, optional): max results.

        Returns:
             List[PortfolioLog]: list of portfolio logs
    """

    query = database.query(PortfolioLog) \
        .filter(PortfolioLog.status == "0") \
        .filter(PortfolioLog.portfolio_id == portfolio.id) \
        .filter(PortfolioLog.transaction_code.in_(transaction_codes))

    if transaction_date_min:
        query = query.filter(PortfolioLog.transaction_date >= transaction_date_min)

    if transaction_date_max:
        query = query.filter(PortfolioLog.transaction_date <= transaction_date_max)

    query.order_by(PortfolioLog.transaction_date)

    if first_result:
        query = query.offset(first_result)

    if max_result:
        query = query.limit(max_result)

    return query.all()


def find_portfolio_log(database: Session, portfolio_log_id: UUID) -> Optional[PortfolioLog]:
    """Finds portfolio log from the database

    Args:
            database (Session): database session
            portfolio_log_id (UUID): portfolio log id
    """
    return database.query(PortfolioLog) \
        .filter(PortfolioLog.id == portfolio_log_id) \
        .one_or_none()


def find_security_by_original_id(database: Session, original_id: str) -> Optional[Security]:
    """Finds security from the database using original_id

    Args:
            database (Session): database session
            original_id (str): original id
    """
    return database.query(Security) \
        .filter(Security.original_id == original_id) \
        .one_or_none()
