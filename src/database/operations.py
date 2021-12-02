from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from .models import Fund, FundRate
from datetime import date


def find_fund(database: Session, id: UUID) -> Optional[Fund]:
    return database.query(Fund) \
        .filter(Fund.id == id) \
        .one_or_none()


def list_funds(database: Session,
               first_result: int,
               max_result: int
               ) -> List[Fund]:
    return database.query(Fund) \
        .order_by(Fund.fund_id)  \
        .offset(first_result) \
        .limit(max_result) \
        .all()


def query_fund_rates(database: Session,
                     fund_id: UUID,
                     rate_date_min: date,
                     rate_date_max: date,
                     first_result: int = 0,
                     max_result: int = 100
                    ) -> List[FundRate]:
    """Queries the fund rate table

    Args:
        database (Session): database session
        fund_id (UUID): fund id
        rate_date_min (date): filter results by rate_date after given date
        rate_date_max (date): filter results by rate_date before given date
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[RATErah]: list of matching RATErah table rows
    """
    return database.query(FundRate) \
        .filter(FundRate.fund_id == fund_id) \
        .filter(FundRate.rate_date >= rate_date_min) \
        .filter(FundRate.rate_date <= rate_date_max) \
        .offset(first_result) \
        .limit(max_result) \
        .order_by(FundRate.rate_date)  \
        .all()


def get_company_rahs(database: Session, ssn: str) -> List[COMPANYrah]:
    """Queries the COMPANYrah table

    Args:
        database (Session): database session
        ssn (str): ssn of user
    Returns:
        List[COMPANYrah]: list of matching COMPANYrah table rows
    """

    return database.query(COMPANYrah).filter(COMPANYrah.SO_SEC_NR == ssn).all()


def get_portfolio(database: Session, com_code: str):
    """Queries the PORTRANSrah, RATELASTrah, SECURITYrah tables

        Args:
            database (Session): database session
            com_code (str): com_code of user
        Returns:
            List[Portfolio]: list of matching Portfolio objects
        """

    portfolio_id = PORTRANSrah.PORID.label("id")
    total_amount = func.sum(PORTRANSrah.AMOUNT * 100).label("totalAmount")
    purchase_total = func.sum(PORTRANSrah.PUR_CVALUE * 100).label("purchaseTotal")
    market_value_total_eur = func.sum(RATELASTrah.RCLOSE * PORTRANSrah.AMOUNT * 100).label("marketValueTotal")
    rate_last_rah_b = aliased(RATELASTrah)
    market_value_total_non_eur = func.sum(RATELASTrah.RCLOSE / rate_last_rah_b.RCLOSE * PORTRANSrah.AMOUNT * 100) \
        .label("marketValueTotal")

    query_eur_funds = database. \
        query(portfolio_id, total_amount, market_value_total_eur, purchase_total) \
        .join(RATELASTrah, PORTRANSrah.SECID == RATELASTrah.SECID) \
        .join(SECURITYrah, PORTRANSrah.SECID == SECURITYrah.SECID) \
        .filter(SECURITYrah.CURRENCY == "EUR") \
        .filter(PORTRANSrah.COM_CODE == com_code) \
        .group_by(portfolio_id)

    query_non_eur_funds = database.query(portfolio_id, total_amount, market_value_total_non_eur, purchase_total) \
        .join(RATELASTrah, PORTRANSrah.SECID == RATELASTrah.SECID) \
        .join(SECURITYrah, PORTRANSrah.SECID == SECURITYrah.SECID) \
        .join(rate_last_rah_b, SECURITYrah.CURRENCY == rate_last_rah_b.SECID) \
        .filter(SECURITYrah.CURRENCY != "EUR") \
        .filter(PORTRANSrah.COM_CODE == com_code) \
        .group_by(portfolio_id)
    query_portfolio = query_eur_funds.union_all(query_non_eur_funds).subquery()
    result = database.query(
        query_portfolio.c.id.label("id"),
        func.sum(query_portfolio.c.totalAmount).label("totalAmount"),
        func.sum(query_portfolio.c.purchaseTotal).label("purchaseTotal"),
        func.sum(query_portfolio.c.marketValueTotal).label("marketValueTotal")).group_by(query_portfolio.c.id) \
        .all()

    return result


def get_com_code_for_portfolio(database: Session, come_codes: [str], portfolio_id: str) -> str:
    """Queries the PORTFOLrah table

        Args:
            database (Session): database session
            come_codes ([str]): list of valid com_codes for the user
            portfolio_id (str): id of Portfolio
        Returns:
            come_code (str) the com_code for the portfolio
        """

    result = database \
        .query(PORTFOLrah.COM_CODE) \
        .filter(PORTFOLrah.COM_CODE.in_(come_codes)) \
        .filter(PORTFOLrah.PORID == portfolio_id) \
        .scalar()
    return result


def get_portfolio_summary(database: Session, por_id: str, start_date: date, end_date: date, trans_codes: [str]):
    """Queries the PORTLOGrah table

        Args:
            database (Session): database session
            trans_codes ([str]): list of valid trans_codes for the operation
            start_date (date): filter results from this date
            end_date (date): filter resultsto this date
            por_id (str): id of Portfolio
        Returns:
            rows of PORTLOGrah
        """

    result = database \
        .query(PORTLOGrah) \
        .filter(PORTLOGrah.TRANS_CODE.in_(trans_codes)) \
        .filter(PORTLOGrah.TRANS_DATE >= start_date) \
        .filter(PORTLOGrah.TRANS_DATE <= end_date) \
        .filter(PORTLOGrah.PORID == por_id) \
        .all()
    return result


def get_portfolio_history():
    pass  # todo development after new database changes
