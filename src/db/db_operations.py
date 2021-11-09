from sqlalchemy.orm import Session

from . import sqlalchemy_models


def get_funds(db: Session, first_result: int = 0, max_result: int = 100):
    # return db.query(sqlalchemy_models.Fund).offset(first_result).limit(max_result).all()
    return []