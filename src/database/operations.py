import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func
from .models import Fund, SecurityRate, Company, PortfolioTransaction, LastRate, Security, Portfolio, PortfolioLog
from spec.models.portfolio import Portfolio as SpecPortfolio
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
               first_result: int,
               max_result: int
               ) -> List[Fund]:
    """Queries the fund table

    Args:
        database (Session): database session
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[Fund]: list of all Fund table rows
    """
    return database.query(Fund) \
        .order_by(Fund.original_id) \
        .offset(first_result) \
        .limit(max_result) \
        .all()


def query_fund_rates(database: Session,
                     fund_id: UUID,
                     rate_date_min: date,
                     rate_date_max: date,
                     first_result: int = 0,
                     max_result: int = 100
                     ) -> List[SecurityRate]:
    """Queries the fund rate table

    Args:
        database (Session): database session
        fund_id (UUID): fund id
        rate_date_min (date): filter results by rate_date after given date
        rate_date_max (date): filter results by rate_date before given date
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[SecurityRate]: list of matching SecurityRate table rows
    """
    return database.query(SecurityRate) \
        .filter(SecurityRate.fund_id == fund_id) \
        .filter(SecurityRate.rate_date >= rate_date_min) \
        .filter(SecurityRate.rate_date <= rate_date_max) \
        .offset(first_result) \
        .limit(max_result) \
        .order_by(SecurityRate.rate_date) \
        .all()


def get_companies(database: Session, ssn: str) -> List[Company]:
    """Queries the company table

    Args:
        database (Session): database session
        ssn (str): ssn of user/ or company id
    Returns:
        List[Company]: list of matching Company table rows
    """

    return database.query(Company).filter(Company.ssn == ssn).all()


def find_portfolio(database: Session, company_code: str) -> List[SpecPortfolio]:
    """Queries the portfolio_transaction, lastrate, security tables

        Args:
            database (Session): database session
            company_code (str): com_code of user
        Returns:
            List[SpecPortfolio]: list of matching Portfolio(spec model) objects
        """

    portfolio_id = PortfolioTransaction.portfolio_id.label("id")
    total_amount = func.sum(PortfolioTransaction.amount).label("totalAmount")
    purchase_total = func.sum(PortfolioTransaction.purchase_c_value).label("purchaseTotal")
    market_value_total_eur = func.sum(LastRate.rate_close * PortfolioTransaction.amount).label("marketValueTotal")
    rate_last_rah_b = aliased(LastRate)
    market_value_total_non_eur = func.sum(
        LastRate.rate_close / rate_last_rah_b.rate_close * PortfolioTransaction.amount) \
        .label("marketValueTotal")

    query_eur_funds = database. \
        query(portfolio_id, total_amount, market_value_total_eur, purchase_total) \
        .join(PortfolioTransaction, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.security_id) \
        .filter(Security.currency == "EUR") \
        .filter(PortfolioTransaction.company_code == company_code) \
        .group_by(portfolio_id)

    query_non_eur_funds = database.query(portfolio_id, total_amount, market_value_total_non_eur, purchase_total) \
        .join(LastRate, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.security_id) \
        .join(rate_last_rah_b, Security.currency == rate_last_rah_b.security_id) \
        .filter(Security.currency != "EUR") \
        .filter(PortfolioTransaction.company_code == company_code) \
        .group_by(portfolio_id)
    query_portfolio = query_eur_funds.union_all(query_non_eur_funds).subquery()
    result = database.query(
        query_portfolio.c.id.label("id"),
        func.sum(query_portfolio.c.totalAmount).label("totalAmount"),
        func.sum(query_portfolio.c.purchaseTotal).label("purchaseTotal"),
        func.sum(query_portfolio.c.marketValueTotal).label("marketValueTotal")).group_by(query_portfolio.c.id) \
        .all()

    return result


def get_portfolio_uuid_from_portfolio_id(database: Session, portfolio_id: str) -> str:
    """Queries the portfolio table

        Args:
            database (Session): database session
            portfolio_id (str): id of Portfolio
        Returns:
             uuid of portfolio (str)
        """
    return database.query(Portfolio.id).filter(Portfolio.portfolio_id == portfolio_id).scalar()


def get_portfolio_id_from_portfolio_uuid(database: Session, portfolio_uuid: UUID) -> str:
    """Queries the portfolio table

        Args:
            database (Session): database session
            portfolio_uuid (str): id of Portfolio
        Returns:
            portfolio_id (str): id of Portfolio
        """
    return database.query(Portfolio.portfolio_id).filter(Portfolio.id == portfolio_uuid).scalar()


def get_company_code_of_portfolio(database: Session, company_codes: [str], portfolio_id: UUID) -> str:
    """Queries the portfolio table

        Args:
            database (Session): database session
            company_codes ([str]): list of valid com_codes for the user
            portfolio_id (str): id of Portfolio
        Returns:
            come_code (str): the com_code for the portfolio
        """

    return database \
        .query(Portfolio.company_code) \
        .filter(Portfolio.company_code.in_(company_codes)) \
        .filter(Portfolio.id == portfolio_id) \
        .scalar()


def get_portfolio_summary(database: Session, portfolio_original_id: str, start_date: date, end_date: date,
                          transaction_codes: [str]) -> List[PortfolioLog]:
    """Queries the portfolio_log table

        Args:
            database (Session): database session
            transaction_codes ([str]): list of valid transaction_code for the operation
            start_date (date): filter results from this date
            end_date (date): filter results to this date
            portfolio_original_id (str): id of Portfolio
        Returns:
             List[PortfolioLog]: rows of portfolio_log
        """

    return database.query(PortfolioLog).filter(PortfolioLog.transaction_code.in_(transaction_codes)).filter(
        PortfolioLog.transaction_date >= start_date.isoformat()).filter(
        PortfolioLog.transaction_date <= end_date.isoformat()).filter(
        PortfolioLog.portfolio_id == portfolio_original_id).all()


def get_portfolio_history():
    pass  # todo development after new database changes
