import os
import logging
import json
from datetime import date

from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import Fund, FundRate
from aiokafka import ConsumerRecord

logger = logging.getLogger(__name__)


class SyncHandler:
    """Handler for Kafka sync messages"""

    def __init__(self):
        """Constructor"""
        url = os.environ["DATABASE_URL"]
        self.engine = create_engine(url)

    async def handle_message(self, record: ConsumerRecord):
        """Handles message from Kafka

        Args:
            record (ConsumerRecord): record
        """
        try:
            topic = record.topic
            logger.info("Handling message to topic: %s", topic)

            message = json.loads(record.value)
            payload = message["payload"]
            before = payload.get("before", None)
            after = payload.get("after", None)

            if topic == "FundSecurities":
                await self.sync_fund_securities(before=before, after=after)
            elif topic == "RATErah":
                await self.sync_raterah(before=before, after=after)
            else:
                logger.warning("Unknown message from topic %s", topic)
        except Exception as e:
            logger.error("Failed to handle Kafka message %s", e)

    async def sync_fund_securities(self, before: Dict, after: Dict):
        """Syncs fund from Kafka message

        Args:
            before (Dict): data before update
            after (Dict): data after update
        """
        with Session(self.engine) as session:
            if after is None:
                self.delete_fund(session, before)
            else:
                self.upsert_fund(session, before, after)

    async def sync_raterah(self, before: Dict, after: Dict):
        """Syncs fund rate from Kafka message

        Args:
            before (Dict): data before update
            after (Dict): data after update
        """
        with Session(self.engine) as session:
            if after is None:
                self.delete_fund_rate(session, before)
            else:
                self.upsert_fund_rate(session, after)

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
            fund_id = before["fundID"]
            fund = session.query(Fund).filter(Fund.fund_id == fund_id).one_or_none()

        if fund is None:
            fund = Fund()
            created = True

        fund.fund_id = after["fundID"]
        fund.security_id = after["securityID"]
        fund.security_name_fi = after["securityName_fi"]
        fund.security_name_sv = after["securityName_sv"]

        session.add(fund)
        session.commit()

        if created:
            logger.info("Created new fund for security %s", fund.security_id)
        else:
            logger.info("Updated fund for security %s", fund.security_id)

    def delete_fund(self, session: Session, before: Dict):
        """Deletes fund according to Kafka message

        Args:
            session (Session): database session
            before (Dict): data before delete
        """
        fund_id = before["fundID"]
        if fund_id:
            session.query(Fund).filter(Fund.fund_id == fund_id).delete()
            session.commit()
            logger.info("Deleted fund with fund id %s", fund_id)

    def upsert_fund_rate(self, session: Session, after: Dict):
        """Updates fund rate from Kafka message

        Args:
            session (Session): database session
            after (Dict): data after update
        """
        fund_rate = None
        created = False

        security_id = after["SECID"]
        if security_id is None:
            raise Exception("Invalid fund rate message, SECID is not defined")

        rdate = after["RDATE"]
        if rdate is None:
            raise Exception("Invalid fund rate message, RDATE is not defined")

        rclose = after["RCLOSE"]
        if rclose is None:
            raise Exception("Invalid fund rate message, RCLOSE is not defined")

        rate_date = date.fromtimestamp(rdate / 1000.0)

        fund: Fund = session.query(Fund) \
            .filter(Fund.security_id == security_id) \
            .one_or_none()

        if fund is None:
            raise Exception("Unable to sync fund rate, fund for SECID %s not foud", security_id)

        fund_rate = session.query(FundRate) \
            .filter(FundRate.fund_id == fund.id) \
            .filter(FundRate.rate_date == rate_date) \
            .one_or_none()

        if fund_rate is None:
            fund_rate = FundRate()
            fund_rate.fund_id = fund.id
            fund_rate.rate_date = rate_date
            created = True

        fund_rate.rate_close = rclose

        session.add(fund_rate)
        session.commit()

        if created:
            logger.info("Created new fund value for %s / %s", security_id, rate_date)
        else:
            logger.info("Updated fund value for %s / %s", security_id, rate_date)

    def delete_fund_rate(self, session: Session, before: Dict):
        """Deletes fund rate according to Kafka message

        Args:
            session (Session): database session
            before (Dict): data before delete
        """

        security_id = before["SECID"]
        if security_id is None:
            raise Exception("Invalid fund rate message, SECID is not defined")

        fund: Fund = session.query(Fund) \
            .filter(Fund.security_id == security_id) \
            .one_or_none()

        if fund is None:
            raise Exception("Unable to sync fund rate, fund for SECID %s not foud", security_id)

        rdate = before["RDATE"]
        if rdate is None:
            raise Exception("Invalid fund rate message, RDATE is not defined")

        rate_date = date.fromtimestamp(rdate / 1000.0)

        session.query(FundRate) \
            .filter(FundRate.fund_id == fund.id) \
            .filter(FundRate.rate_date == rate_date) \
            .delete()

        session.commit()
        logger.info("Deleted fund rate for %s / %s", security_id, rate_date)
