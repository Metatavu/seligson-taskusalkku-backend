import os
import logging
import json
from datetime import date

from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from aiokafka import ConsumerRecord

from database.models import Security, SecurityRate

logger = logging.getLogger(__name__)


class SyncException(Exception):
    pass

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

            if topic == "TABLE_RATE":
                await self.sync_rate(before=before, after=after)
            else:
                logger.warning("Unknown message from topic %s", topic)
        except Exception as e:
            logger.error("Failed to handle Kafka message %s", e)

    async def sync_rate(self, before: Dict, after: Dict):
        """Syncs fund rate from Kafka message

        Args:
            before: data before
            after: data after
        """
        with Session(self.engine) as session:
            if after is None:
                self.delete_security_rate(session, before)
            else:
                self.upsert_security_rate(session, before, after)

    def upsert_security_rate(self, session: Session, before: Dict, after: Dict):
        """Updates fund rate from Kafka message

        Args:
            session (Session): database session
            before (Dict): data before update
            after (Dict): data after update
        """
        created = False

        security_original_id = after["SECID"]
        if security_original_id is None:
            raise SyncException("Invalid fund rate message, SECID is not defined")

        rdate = after["RDATE"]
        if rdate is None:
            raise SyncException("Invalid fund rate message, RDATE is not defined")

        rclose = after["RCLOSE"]
        if rclose is None:
            raise SyncException("Invalid fund rate message, RCLOSE is not defined")

        rate_date = date.fromtimestamp(rdate / 1000.0)

        security: Security = session.query(Security) \
            .filter(Security.original_id == security_original_id) \
            .one_or_none()

        if security is None:
            raise SyncException("Unable to sync security rate, security for SECID %s not foud", security_original_id)

        security_rate = session.query(SecurityRate) \
            .filter(SecurityRate.security == security) \
            .filter(SecurityRate.rate_date == rate_date) \
            .one_or_none()

        if security_rate is None:
            security_rate = SecurityRate()
            security_rate.security = security
            security_rate.rate_date = rate_date
            created = True

        security_rate.rate_close = rclose

        session.add(security_rate)
        session.commit()

        if created:
            logger.info("Created new security value for %s / %s", security_original_id, rate_date)
        else:
            logger.info("Updated security value for %s / %s", security_original_id, rate_date)

    def delete_security_rate(self, session: Session, before: Dict):
        """Deletes fund rate according to Kafka message

        Args:
            session (Session): database session
            before (Dict): data before delete
        """

        security_original_id = before["SECID"]
        if security_original_id is None:
            raise SyncException("Invalid fund rate message, SECID is not defined")

        security: Security = session.query(Security) \
            .filter(Security.original_id == security_original_id) \
            .one_or_none()

        if security is None:
            raise SyncException("Unable to sync security rate, security for SECID %s not foud", security_original_id)

        rdate = before["RDATE"]
        if rdate is None:
            raise SyncException("Invalid fund rate message, RDATE is not defined")

        rate_date = date.fromtimestamp(rdate / 1000.0)

        session.query(SecurityRate) \
            .filter(SecurityRate.security == security) \
            .filter(SecurityRate.rate_date == rate_date) \
            .delete()

        session.commit()
        logger.info("Deleted security rate for %s / %s", security_original_id, rate_date)
