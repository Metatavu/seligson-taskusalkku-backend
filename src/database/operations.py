from typing import List
from sqlalchemy.orm import Session
from .sqlalchemy_models import RATErah


def query_raterah(database: Session, secid: str, first_result: int = 0, max_result: int = 100) -> List[RATErah]:
    """Queries the RATErah table

    Args:
        database (Session): database session
        secid (str): secid
        first_result (int, optional): first result. Defaults to 0.
        max_result (int, optional): max results. Defaults to 100.

    Returns:
        List[RATErah]: list of matching RATErah table rows
    """
    return database.query(RATErah) \
        .filter(RATErah.SECID == secid) \
        .offset(first_result) \
        .limit(max_result) \
        .all()
