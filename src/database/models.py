from uuid import uuid4

from database.sqlalchemy_uuid import SqlAlchemyUuid
from sqlalchemy import Column, DECIMAL, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Fund(Base):
    __tablename__ = 'Fund'

    id = Column(SqlAlchemyUuid, primary_key=True, default=uuid4)
    fundId = Column(Integer, index=True, unique=True)
    securityId = Column(String(24), index=True, unique=True)
    securityNameFi = Column(String(191), nullable=False)
    securityNameSv = Column(String(191), nullable=False)
    classType = Column(String(191), nullable=False)
    minimumPurchase = Column(DECIMAL(19, 6), nullable=False, default=0.000)
