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
