from typing import List
from sqlalchemy.orm import Session
from .sqlalchemy_models import RATErah
from datetime import date


def query_raterah(database: Session,
                  secid: str,
                  rdate_min: date,
                  rdate_max: date,
                  first_result: int = 0,
                  max_result: int = 100
                  ) -> List[RATErah]:
    """Queries the RATErah table

    Args:
        database (Session): database session
        secid (str): secid
        rdate_min (date): filter results by rdate after given date
        rdate_max (date): filter results by rdate before given date
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[RATErah]: list of matching RATErah table rows
    """
    return database.query(RATErah) \
        .filter(RATErah.SECID == secid) \
        .filter(RATErah.RDATE >= rdate_min) \
        .filter(RATErah.RDATE <= rdate_max) \
        .offset(first_result) \
        .limit(max_result) \
        .order_by(RATErah.RDATE)  \
        .all()
