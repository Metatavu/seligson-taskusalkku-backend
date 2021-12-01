import os
import logging
import json

from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import Fund
from aiokafka import ConsumerRecord

logger = logging.getLogger(__name__)


class SyncHandler:

    def __init__(self):
        """Constructor"""
        url = os.environ["DATABASE_URL"]
        self.engine = create_engine(url)

    async def sync_fund_securities(self, record: ConsumerRecord):
        """Syncs fund from Kafka message

        Args:
            record (ConsumerRecord): record
        """
        with Session(self.engine) as session:
            message = json.loads(record.value)

            payload = message["payload"]
            before = payload["before"]
            after = payload["after"]

            if after is None:
                self.delete_fund(session, before)
            else:
                self.upsert_fund(session, before, after)

    def delete_fund(self, session: Session, before: Dict):
        """Deletes fund according to Kafka message

        Args:
            session (Session): database session
            before (Dict): data before delete
        """
        fund_id = before["fundID"]
        if fund_id:
            session.query(Fund).filter(Fund.fundId == fund_id).delete()
            session.flush()
            logger.info("Deleted fund with fundId {fundId}")

    def upsert_fund(self, session: Session, before: Dict, after: Dict):
        """Updates fund from Kafka message

        Args:
            session (Session): database session
            before (Dict): data before update
            after (Dict): data after update
        """
        fund = None
        created = False

        if before is not None:
            fund = session.query(Fund).filter(Fund.fundId == before["fundID"])

        if fund is None:
            fund = Fund()
            created = True

        fund.fundId = after["fundID"]
        fund.securityId = after["securityID"]
        fund.securityNameFi = after["securityName_fi"]
        fund.securityNameSv = after["securityName_sv"]
        fund.classType = after["class"]
        fund.minimumPurchase = 0

        session.add(fund)
        session.flush()

        if created:
            logger.info(f"Created new fund with fundId {fund.fundId}")
        else:
            logger.info(f"Updated fund with fundId {fund.fundId}")
