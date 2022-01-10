import os
import logging
from decimal import Decimal

from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, and_
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session
from typing import Optional
from database import models as destination_models
from datetime import datetime, date

logger = logging.getLogger(__name__)


class MigrationException(Exception):
    """
    Migration exception
    """
    pass


class AbstractMigrationTask(ABC):
    """
    Abstract migration task
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns task's name
        Returns: task's name
        """
        ...

    @abstractmethod
    def up_to_date(self, backend_session: Session) -> bool:
        """
        Returns whether task is already up-to-date or not
        Args:
            backend_session: backend database session

        Returns:
            whether task is already up-to-date or not
        """
        ...

    @abstractmethod
    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        """
        Runs migration task
        Args:
            backend_session: backend database session
            timeout: timeout

        Returns:
            count of updated entries
        """
        ...

    @staticmethod
    def print_message(message: str):
        """
        Prints message
        Args:
            message: message
        """
        logger.warning(message)

    def should_timeout(self, timeout: datetime) -> bool:
        """
        Returns whether task should time out
        Returns: whether task should time out
        """
        result = timeout < datetime.now()

        if result:
            self.print_message("Timeout reached, stopping...")

        return result

    @staticmethod
    def get_security_by_original_id(session, original_security_id) -> Optional[destination_models.Security]:
        """
        Finds a security by original id
        Args:
            session: backend session
            original_security_id: original id

        Returns: security or None if not found
        """
        return session.query(destination_models.Security).filter(
            destination_models.Security.original_id == original_security_id).one_or_none()

    @staticmethod
    def get_fund_id_by_original_id(backend_session: Session, original_id: str) -> Optional[UUID]:
        """
        Finds fund id by fund original id
        Args:
            backend_session: backend session
            original_id: original id

        Returns: fund id or None if not found
        """
        return backend_session.query(destination_models.Fund.id).filter(
            destination_models.Fund.original_id == original_id).scalar()


class AbstractSalkkuTask(AbstractMigrationTask, ABC):
    """
    Abstract base class for salkku migrations
    """

    @staticmethod
    def get_salkku_database_engine() -> MockConnection:
        """
        Initializes salkku database engine

        Returns:
            engine
        """
        salkku_database_url = os.environ.get("SALKKU_DATABASE_URL", "")

        if not salkku_database_url:
            raise MigrationException("SALKKU_DATABASE_URL environment variable is not set")
        else:
            return create_engine(salkku_database_url)


class AbstractFundsTask(AbstractMigrationTask, ABC):
    """
    Abstract base class for fund migrations
    """

    @staticmethod
    def get_funds_database_engine() -> MockConnection:
        """
        Initializes funds database engine

        Returns:
            engine
        """
        database_url = os.environ.get("FUNDS_DATABASE_URL", "")

        if not database_url:
            raise MigrationException("FUNDS_DATABASE_URL environment variable is not set")
        else:
            return create_engine(database_url)


class MigrateSecuritiesTask(AbstractFundsTask):
    """
    Migration task for securities
    """

    def get_name(self):
        return "securities"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_security_count = backend_session.execute(statement="SELECT COUNT(ID) FROM security").fetchone()
            funds_security_count = funds_session.execute(statement="SELECT COUNT(SECID) FROM TABLE_SECURITY").fetchone()
            return backend_security_count >= funds_security_count

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        with Session(self.get_funds_database_engine()) as funds_session:

            security_rows = self.list_security_rows(funds_session=funds_session)
            for security_row in security_rows:
                original_security_id = security_row.SECID
                original_fund_id = security_row.SORTNAME
                fund_id = None

                if original_fund_id is not None and original_fund_id.isnumeric():
                    fund_id = self.get_fund_id_by_original_id(backend_session, original_fund_id)
                    if not fund_id:
                        self.print_message(f"Warning: Could not find fund with original id {original_fund_id}")

                existing_security: destination_models.Security = self.get_security_by_original_id(
                    session=backend_session, original_security_id=original_security_id)

                self.upsert_security(backend_session=backend_session,
                                     security=existing_security,
                                     original_id=original_security_id,
                                     fund_id=fund_id,
                                     currency=security_row.CURRENCY,
                                     name_fi=security_row.NAME1,
                                     name_sv=security_row.NAME2)

                synchronized_count = synchronized_count + 1

            return synchronized_count

    @staticmethod
    def list_security_rows(funds_session: Session):
        """
        Lists securities from funds database
        Args:
            funds_session: Funds database session

        Returns: securities from funds database
        """
        statement = "SELECT SECID, SORTNAME, CURRENCY, NAME1, NAME2 FROM TABLE_SECURITY"
        return funds_session.execute(statement=statement)

    @staticmethod
    def upsert_security(backend_session: Session, security, original_id, fund_id=None, currency="", name_fi="",
                        name_sv="") -> destination_models.Security:
        new_security = security if security else destination_models.Security()
        new_security.original_id = original_id
        new_security.fund_id = fund_id
        new_security.currency = currency
        new_security.name_fi = name_fi
        new_security.name_sv = name_sv
        backend_session.add(new_security)
        return new_security


class MigrateSecurityRatesTask(AbstractFundsTask):
    """
    Migration task for security rates
    """

    def get_name(self):
        return "securityrate"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = backend_session.execute(statement="SELECT COUNT(ID) FROM security_rate").fetchone()
            funds_count = funds_session.execute(statement="SELECT COUNT(*) FROM TABLE_RATE").fetchone()
            return backend_count >= funds_count

    @staticmethod
    def get_last_backend_date(backend_session: Session) -> Optional[datetime]:
        return backend_session.execute(statement="SELECT max(rate_date) FROM security_rate").fetchone()[0]

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        offset = 0
        batch = 1000

        with Session(self.get_funds_database_engine()) as funds_session:
            last_backend_date = self.get_last_backend_date(backend_session=backend_session)
            if not last_backend_date:
                last_backend_date = date(1970, 1, 1)

            while not self.should_timeout(timeout=timeout):
                self.print_message(f"Migrating rates from offset {offset}")

                rate_rows = self.list_rates(
                    funds_session=funds_session,
                    rdate=last_backend_date,
                    offset=offset,
                    limit=batch
                )

                for rate_row in rate_rows:
                    original_security_id = rate_row.SECID

                    security: destination_models.Security = self.get_security_by_original_id(
                        session=backend_session,
                        original_security_id=original_security_id
                    )

                    if not security:
                        self.print_message(f"Warning: Could not find security with original id {original_security_id}")
                    else:
                        has_rate = offset == 0 and self.has_security_rate(
                            backend_session=backend_session,
                            security=security,
                            rate_date=rate_row.RDATE
                        )

                        if not has_rate:
                            self.insert_security_rate(
                                backend_session=backend_session,
                                security=security,
                                rate_date=rate_row.RDATE,
                                rate_close=rate_row.RCLOSE
                            )

                            synchronized_count = synchronized_count + 1

                offset += batch

            return synchronized_count

    @staticmethod
    def list_rates(funds_session: Session, rdate: datetime, limit: int, offset: int):
        """
        Lists rates from funds database
        Args:
            funds_session: Funds database session
            rdate: min rdate
            limit: max results
            offset: offset

        Returns: rates from funds database
        """
        return funds_session.execute('SELECT SECID, RDATE, RCLOSE FROM TABLE_RATE WHERE RDATE >= :rdate '
                                     'ORDER BY RDATE, SECID OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY',
                                     {
                                         "limit": limit,
                                         "offset": offset,
                                         "rdate": rdate.isoformat()
                                     })

    @staticmethod
    def has_security_rate(backend_session: Session, security: destination_models.Security, rate_date: date) -> bool:
        """
        Returns whether rate exists for given security and date
        Args:
            backend_session: backend database session
            security: security
            rate_date: date

        Returns: whether rate exists for given security and date
        """
        return backend_session.query(destination_models.SecurityRate.id)\
            .filter( and_(destination_models.SecurityRate.security_id == security.id,
                          destination_models.SecurityRate.rate_date == rate_date))\
            .one_or_none()

    @staticmethod
    def insert_security_rate(backend_session: Session, security: destination_models.Security, rate_date: date,
                             rate_close: Decimal) -> destination_models.SecurityRate:
        """
        Inserts new row into security rate table
        Args:
            backend_session: backend database session
            security: security
            rate_date: date
            rate_close: close
        """
        security_rate = destination_models.SecurityRate()
        security_rate.security = security
        security_rate.rate_date = rate_date
        security_rate.rate_close = rate_close
        backend_session.add(security_rate)
        return security_rate


class MigrateFundsTask(AbstractMigrationTask):
    """
    Migration task for funds
    """

    def __init__(self):
        """
        Constructor
        """
        self.kiid_engine = self.get_kiid_engine()

    def get_name(self):
        return "funds"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.kiid_engine) as kiid_session:
            backend_fund_count = backend_session.execute(statement="SELECT COUNT(id) FROM fund").fetchone()
            kiid_fund_count = kiid_session.execute(statement="SELECT COUNT(ID) FROM FUND").fetchone()
            return backend_fund_count >= kiid_fund_count

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        with Session(self.kiid_engine) as kiid_session:

            fund_rows = self.list_fund_rows(kiid_session=kiid_session)
            for fund_row in fund_rows:
                fund_id = fund_row.ID

                fund: destination_models.Fund = backend_session.query(destination_models.Fund) \
                    .filter(destination_models.Fund.original_id == fund_id) \
                    .one_or_none()

                if not fund:
                    fund = destination_models.Fund()
                    fund.original_id = fund_id

                if fund_row.URL_EN:
                    fund.kiid_url_en = fund_row.URL_EN

                if fund_row.URL_FI:
                    fund.kiid_url_fi = fund_row.URL_FI

                if fund_row.URL_SV:
                    fund.kiid_url_sv = fund_row.URL_SV

                if fund_row.RISK_LEVEL:
                    fund.risk_level = fund_row.RISK_LEVEL

                backend_session.add(fund)
                synchronized_count = synchronized_count + 1

            return synchronized_count

    @staticmethod
    def list_fund_rows(kiid_session: Session):
        """
        Lists rows from the kiid funds table
        Args:
            kiid_session: KIID database session

        Returns: rows from the kiid funds table
        """
        risk_query = "SELECT TOP 1 risk_level FROM TextContent WHERE fund_name = NAME_KIID ORDER BY modification_time"
        statement = f"SELECT ID, URL_FI, URL_SV, URL_EN, ({risk_query}) as RISK_LEVEL FROM FUND"
        return kiid_session.execute(statement=statement)

    @staticmethod
    def get_kiid_engine() -> MockConnection:
        """
        Initializes KIID database engine
        """
        kiid_database_url = os.environ.get("KIID_DATABASE_URL", "")
        if not kiid_database_url:
            raise MigrationException("KIID_DATABASE_URL environment variable is not set")
        else:
            return create_engine(kiid_database_url)
