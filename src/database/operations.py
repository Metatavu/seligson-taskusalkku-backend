from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func
from .models import Fund, SecurityRate, Company, PortfolioTransaction, LastRate, Security, Portfolio, PortfolioLog
from datetime import date


@dataclass
class PortfolioValues:
    """Data class for portfolio values query result"""
    total_amount: str
    purchase_total: str
    market_value_total: str


@dataclass
class PortfolioSecurityValues:
    """Data class for portfolio security values query result"""
    security_id: UUID
    total_amount: str
    purchase_total: str
    market_value_total: str


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


def list_securities_with_fund(database: Session,
                              first_result: int,
                              max_result: int
                              ) -> List[Security]:
    """Lists securities with not null fund

    Args:
        database (Session): database session
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[Security]: list of security with fund_id
    """
    return database.query(Security) \
        .filter(Security.fund_id.is_not(None)) \
        .order_by(Security.original_id) \
        .offset(first_result) \
        .limit(max_result) \
        .all()


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


def get_companies(database: Session, ssn: str) -> List[Company]:
    """Queries the company table

    Args:
        database (Session): database session
        ssn (str): ssn of user/ or company id
    Returns:
        List[Company]: list of matching Company table rows
    """

    return database.query(Company).filter(Company.ssn == ssn).all()


def find_portfolio(database: Session, portfolio_id: UUID) -> Optional[Portfolio]:
    """Finds portfolio from the database

    Args:
            database (Session): database session
            portfolio_id (UUID): portfolio id
    """
    return database.query(Portfolio) \
        .filter(Portfolio.id == portfolio_id) \
        .one_or_none()


def find_portfolio_values(database: Session, portfolio: Portfolio) -> PortfolioValues:
    """Queries the portfolio values from database

        Args:
            database (Session): database session
            portfolio (Portfolio): portfolio
        Returns:
            PortfolioValues: portfolio values
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
        .join(Security, PortfolioTransaction.security_id == Security.id) \
        .filter(Security.currency == "EUR") \
        .filter(PortfolioTransaction.portfolio == portfolio) \
        .group_by(portfolio_id)

    query_non_eur_funds = database.query(portfolio_id, total_amount, market_value_total_non_eur, purchase_total) \
        .join(LastRate, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.id) \
        .join(rate_last_rah_b, Security.currency == rate_last_rah_b.security_id) \
        .filter(Security.currency != "EUR") \
        .filter(PortfolioTransaction.portfolio == portfolio) \
        .group_by(portfolio_id)

    query_portfolio = query_eur_funds.union_all(query_non_eur_funds).subquery()

    result = database.query(
        query_portfolio.c.id.label("id"),
        func.sum(query_portfolio.c.totalAmount).label("totalAmount"),
        func.sum(query_portfolio.c.purchaseTotal).label("purchaseTotal"),
        func.sum(query_portfolio.c.marketValueTotal).label("marketValueTotal")) \
        .one()

    return PortfolioValues(
        total_amount=result.totalAmount,
        purchase_total=result.purchaseTotal,
        market_value_total=result.marketValueTotal
    )


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

    return database.query(PortfolioLog).filter(PortfolioLog.transaction_code.in_(transaction_codes)).filter(
        PortfolioLog.transaction_date >= start_date.isoformat()).filter(
        PortfolioLog.transaction_date <= end_date.isoformat()).filter(
        PortfolioLog.portfolio == portfolio).all()


def get_portfolio_security_values(database: Session, portfolio: Portfolio) -> List[PortfolioSecurityValues]:
    """ Queries for portfolio securities

        Args:
            database (Session): database session
            portfolio (Portfolio): portfolio
        Returns:
             List[PortfolioSecurityValues]: list of portfolio securities
    """
    eur_security_id = PortfolioTransaction.security_id.label("security_id")
    eur_total_amount = func.sum(PortfolioTransaction.amount).label("totalAmount")
    eur_purchase_total = func.sum(PortfolioTransaction.purchase_c_value).label("purchaseTotal")
    eur_market_value = func.sum(LastRate.rate_close * PortfolioTransaction.amount).label("marketValueTotal")

    eur_query = database.query(Portfolio, eur_security_id, eur_total_amount, eur_purchase_total, eur_market_value) \
        .join(PortfolioTransaction, Portfolio.id == PortfolioTransaction.portfolio_id) \
        .join(LastRate, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.id) \
        .filter(Portfolio.id == portfolio.id) \
        .filter(Security.currency == "EUR") \
        .group_by(Security.id)

    security_cur: Security = aliased(Security)
    last_rate_cur: LastRate = aliased(LastRate)

    not_eur_security_id = PortfolioTransaction.security_id.label("security_id")
    not_eur_total_amount = func.sum(PortfolioTransaction.amount).label("totalAmount")
    not_eur_purchase_total = func.sum(PortfolioTransaction.purchase_c_value).label("purchaseTotal")
    not_eur_market_value = func.sum(LastRate.rate_close / last_rate_cur.rate_close *
                                    PortfolioTransaction.amount).label("marketValueTotal")

    not_eur_query = database.query(Portfolio, not_eur_security_id, not_eur_total_amount, not_eur_purchase_total,
                                   not_eur_market_value) \
        .join(PortfolioTransaction, Portfolio.id == PortfolioTransaction.portfolio_id) \
        .join(LastRate, PortfolioTransaction.security_id == LastRate.security_id) \
        .join(Security, PortfolioTransaction.security_id == Security.id) \
        .join(security_cur, security_cur.currency == security_cur.original_id) \
        .join(last_rate_cur, security_cur.id == last_rate_cur.security_id) \
        .filter(Portfolio.id == portfolio.id) \
        .filter(Security.currency != "EUR") \
        .group_by(Security.id)

    rows = eur_query.union_all(not_eur_query).all()
    results = []

    for row in rows:
        results.append(
            PortfolioSecurityValues(
                security_id=row.security_id,
                total_amount=row.totalAmount,
                purchase_total=row.purchaseTotal,
                market_value_total=row.marketValueTotal,
            )
        )

    return results


def get_portfolio_logs(database: Session,
                       portfolio: Portfolio,
                       transaction_codes: List[str],
                       transaction_date_min: Optional[date],
                       transaction_date_max: Optional[date],
                       first_result: int = 0,
                       max_result: int = 100
                       ) -> List[PortfolioLog]:
    """ Queries for portfolio logs

        Args:
            database (Session): database session
            portfolio (Portfolio): portfolio
            transaction_codes (List[str]): filter by transaction codes
            transaction_date_min (date): filter results by transaction_date after given date
            transaction_date_max (date): filter results by transaction_date before given date
            first_result (int, optional): first result. Defaults to 0.
            max_result (int, optional): max results. Defaults to 100.

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

    return query \
        .order_by(PortfolioLog.transaction_date) \
        .offset(first_result) \
        .limit(max_result) \
        .all()


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


def get_portfolio_history():
    pass  # todo development after new database changes
