from uuid import uuid4

from .sqlalchemy_uuid import SqlAlchemyUuid
from sqlalchemy import Column, DECIMAL, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Fund(Base):
    __tablename__ = 'fund'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    fund_id = Column(Integer, index=True, unique=True)
    security_id = Column(String(24), index=True, unique=True)
    security_name_fi = Column(String(191), nullable=False)
    security_name_sv = Column(String(191), nullable=False)
    rates = relationship("FundRate", back_populates="fund", lazy=True)


class FundRate(Base):
    __tablename__ = 'fund_rate'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    fund_id = Column("fund_id", SqlAlchemyUuid, ForeignKey('fund.id'))
    rate_date = Column("rate_date", Date)
    rate_close = Column(DECIMAL(19, 6), nullable=False)
    fund = relationship("Fund", back_populates="rates", lazy=True)
