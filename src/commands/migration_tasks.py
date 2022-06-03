import os
import logging
import re

from decimal import Decimal

from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, and_, func, text, Integer, DECIMAL
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, TypedDict

from database import models as destination_models
from datetime import datetime, date, timedelta

from .migration_exceptions import MigrationException, MissingSecurityException, \
    MissingCompanyException, MissingPortfolioException

FUND_GROUPS = ["PASSIVE", "ACTIVE", "BALANCED", "FIXED_INCOME", "DIMENSION", "SPILTAN"]

TIMED_OUT = "Timed out."

logger = logging.getLogger(__name__)


class TaskOptions(TypedDict):
    security: Optional[str]


class AbstractMigrationTask(ABC):
    """
    Abstract migration task
    """
    options: TaskOptions

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns task's name
        Returns: task's name
        """
        ...

    def prepare(self, backend_session: Session):
        """
        Task can override this method to perform preparations for the task.
        Method is executed before up_to_date and migrate functions.
        Args:
            backend_session:

        Returns:

        """
        pass

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
    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        """
        Runs migration task
        Args:
            backend_session: backend database session
            timeout: timeout
            force_recheck: Whether task should be forced to recheck all entities

        Returns:
            count of updated entries
        """
        ...

    @abstractmethod
    def verify(self, backend_session: Session) -> bool:
        """
        Verifies data correctness

        Args:
            backend_session: backend database session

        Returns:
            whether data is correct or not
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

    @staticmethod
    def should_timeout(timeout: datetime) -> bool:
        """
        Returns whether task should time out
        Returns: whether task should time out
        """
        return timeout < datetime.now()

    @staticmethod
    def get_company_by_original_id(backend_session: Session, original_id: str) -> Optional[destination_models.Company]:
        """
        Finds a company by original id
        Args:
            backend_session: backend session
            original_id: original id

        Returns: security or None if not found
        """
        return backend_session.query(destination_models.Company).filter(
            destination_models.Company.original_id == original_id).one_or_none()

    @staticmethod
    def get_security_by_original_id(backend_session: Session, original_id) -> Optional[destination_models.Security]:
        """
        Finds a security by original id
        Args:
            backend_session: backend session
            original_id: original id

        Returns: security or None if not found
        """
        return backend_session.query(destination_models.Security).filter(
            destination_models.Security.original_id == original_id).one_or_none()

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

    @staticmethod
    def get_portfolio_id_by_original_id(backend_session: Session, original_id: str) -> Optional[UUID]:
        """
        Finds portfolio id by original id
        Args:
            backend_session: backend session
            original_id: original id

        Returns: portfolio id or None if not found
        """
        return backend_session.query(destination_models.Portfolio.id).filter(
            destination_models.Portfolio.original_id == original_id).scalar()

    @staticmethod
    def list_portfolios_by_company(backend_session: Session, company_id: UUID) -> List[destination_models.Portfolio]:
        return backend_session.query(destination_models.Portfolio).filter(
            destination_models.Portfolio.company_id == company_id).all()

    @staticmethod
    def list_securities(backend_session: Session) -> List[destination_models.Security]:
        """
        Lists all securities
        Args:
            backend_session: backend database session

        Returns: all securities
        """
        return backend_session.query(destination_models.Security).all()

    @staticmethod
    def round_datetime_to_seconds(value: datetime) -> datetime:
        """
        Rounds datetime to seconds
        Args:
            value: datetime

        Returns: datetime rounded to seconds
        """
        if value.microsecond >= 500_000:
            value += timedelta(seconds=1)
        return value.replace(microsecond=0)


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

    @staticmethod
    def get_excluded_portfolio_ids_query():
        """
        Returns exclude query for excluded porids
        Returns: exclude query for excluded porids
        """
        return "SELECT DISTINCT P.PORID " \
               "FROM TABLE_PORTFOL P " \
               "INNER JOIN TABLE_PORCLASSDEF D ON P.COM_CODE = D.COM_CODE " \
               "AND P.PORID = D.PORID AND D.PORCLASS IN (3, 4, 5)"

    @staticmethod
    def list_backend_companies(backend_session: Session):
        """
        Lists companies from backend database
        Args:
            backend_session: Backend database session

        Returns: companies from backend database
        """
        return backend_session.query(destination_models.Company).all()


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


class MigrateSecuritiesTask(AbstractFundsTask):
    """
    Migration task for securities
    """

    def get_name(self):
        return "securities"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            fund_count = self.count_fund_security_rows(funds_session=funds_session)
            security_count = self.count_backend_security_rows(backend_session=backend_session)

            if fund_count != security_count:
                return False

            max_date_backend = self.get_backend_last_update_date(backend_session=backend_session)
            max_date_source = self.get_fund_last_update_date(funds_session=funds_session)
            if max_date_source is None or max_date_backend is None:
                return False

            funds_updated = self.round_datetime_to_seconds(max_date_source.LAST_UPDATE)
            backend_updated = self.round_datetime_to_seconds(max_date_backend.last_update)

            return backend_updated == funds_updated

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0
        with Session(self.get_funds_database_engine()) as funds_session:

            fund_security_rows = self.list_fund_security_rows(funds_session=funds_session)
            fund_security_ids = []

            for fund_security_row in fund_security_rows:
                original_security_id = fund_security_row.SECID
                fund_security_ids.append(original_security_id)
                original_fund_id = fund_security_row.SORTNAME
                fund_id = None

                if original_fund_id is not None and original_fund_id.isnumeric():
                    fund_id = self.get_fund_id_by_original_id(backend_session, original_fund_id)
                    if not fund_id:
                        self.print_message(f"Warning: Could not find fund with original id {original_fund_id}")

                existing_security: destination_models.Security = self.get_security_by_original_id(
                    backend_session=backend_session, original_id=original_security_id)

                fund_updated = fund_security_row.UPD_DATE
                if fund_updated is None:
                    fund_updated = datetime(1970, 1, 1, 0, 0)

                backend_updated = existing_security.updated if existing_security else None
                if backend_updated is None:
                    backend_updated = datetime(1970, 1, 1, 0, 0)

                if not existing_security or existing_security.name_en is None or \
                        self.round_datetime_to_seconds(fund_updated) > \
                        self.round_datetime_to_seconds(backend_updated):
                    self.upsert_security(backend_session=backend_session,
                                         security=existing_security,
                                         original_id=original_security_id,
                                         fund_id=fund_id,
                                         currency=fund_security_row.CURRENCY,
                                         name_fi=fund_security_row.NAME1,
                                         name_sv=fund_security_row.NAME2,
                                         name_en=fund_security_row.NAME3,
                                         series_id=fund_security_row.SERIES_ID,
                                         updated=fund_updated)

                    synchronized_count = synchronized_count + 1

            backend_original_ids = self.list_backend_security_original_ids(backend_session=backend_session)

            removed_original_ids = []
            for original_id in backend_original_ids:
                if original_id not in fund_security_ids:
                    removed_original_ids.append(original_id)

            if len(removed_original_ids) > 0:
                self.print_message(f"Deleting securities with original_ids {removed_original_ids}")

                synchronized_count = synchronized_count + backend_session.query(destination_models.Security) \
                    .filter(destination_models.Security.original_id.in_(removed_original_ids)) \
                    .delete(synchronize_session=False)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            fund_securities = self.list_fund_security_rows(funds_session=funds_session).all()
            backend_securities = self.list_backend_securities(backend_session=backend_session)
            backend_security_map = {x.original_id: x for x in backend_securities}

            if len(backend_securities) != len(fund_securities):
                self.print_message(f"Warning: Security count mismatch: "
                                   f"{len(backend_securities)} != {len(fund_securities)} ")
                return False

            for fund_security in fund_securities:
                if fund_security.SECID not in backend_security_map:
                    self.print_message(f"Warning: Security {fund_security.SECID} not found in backend")
                    return False

                backend_security = backend_security_map[fund_security.SECID]
                expected_fund_id = self.get_fund_id_by_original_id(
                    backend_session=backend_session,
                    original_id=fund_security.SORTNAME
                )

                if expected_fund_id != backend_security.fund_id:
                    self.print_message(f"Warning: Security fund mismatch for security {fund_security.SECID} ")
                    return False

                if fund_security.CURRENCY != backend_security.currency:
                    self.print_message(f"Warning: Security currency mismatch for security {fund_security.SECID}"
                                       f" {fund_security.CURRENCY} != {backend_security.currency}")
                    return False

                if fund_security.NAME1 != backend_security.name_fi:
                    self.print_message(f"Warning: Security name_fi mismatch for security {fund_security.SECID}"
                                       f" {fund_security.NAME1} != {backend_security.name_fi}")
                    return False

                if fund_security.NAME2 != backend_security.name_sv:
                    self.print_message(f"Warning: Security name_sv mismatch for security {fund_security.SECID}"
                                       f" {fund_security.NAME2} != {backend_security.name_fi}")
                    return False

                if fund_security.NAME3 != backend_security.name_en:
                    self.print_message(f"Warning: Security name_en mismatch for security {fund_security.SECID}"
                                       f" {fund_security.NAME3} != {backend_security.name_fi}")
                    return False

                if fund_security.SERIES_ID != backend_security.series_id:
                    self.print_message(f"Warning: Security series_id mismatch for security {fund_security.SECID}"
                                       f" {fund_security.SERIES_ID} != {backend_security.series_id}")
                    return False

            self.print_message(f"Verified all securities")

        return True

    @staticmethod
    def count_fund_security_rows(funds_session: Session):
        """
        Counts securities from funds database
        Args:
            funds_session: Funds database session

        Returns: count from funds database
        """
        statement = "SELECT COUNT(SECID) FROM TABLE_SECURITY"
        return funds_session.execute(statement=statement).scalar()

    @staticmethod
    def count_backend_security_rows(backend_session: Session):
        """
        Counts securities from backend database
        Args:
            backend_session: Backend database session

        Returns: count from backend database
        """
        return backend_session.execute(statement="SELECT COUNT(id) FROM security").scalar()

    @staticmethod
    def list_fund_security_rows(funds_session: Session):
        """
        Lists securities from funds database
        Args:
            funds_session: Funds database session

        Returns: securities from funds database
        """
        statement = "SELECT SECID, SORTNAME, CURRENCY, NAME1, NAME2, NAME3, SERIES_ID, UPD_DATE FROM TABLE_SECURITY"
        return funds_session.execute(statement=statement)

    @staticmethod
    def get_fund_last_update_date(funds_session: Session):
        """
        get last update date of security table from funds database
        Args:
            funds_session: Funds database session

        Returns: date from funds database
        """
        statement = "SELECT MAX(UPD_DATE) AS LAST_UPDATE FROM TABLE_SECURITY"
        return funds_session.execute(statement=statement).one_or_none()

    @staticmethod
    def get_backend_last_update_date(backend_session: Session):
        """
        get last update date of security table from backend database
        Args:
            backend_session: Backend database session

        Returns: date from backend database
        """
        return backend_session.query(func.max(destination_models.Security.updated).label("last_update")).one_or_none()

    @staticmethod
    def list_backend_securities(backend_session: Session) -> List[destination_models.Security]:
        """
        Lists original ids from backend database
        Args:
            backend_session: Backend database session

        Returns: original ids
        """
        return backend_session.query(destination_models.Security).all()

    @staticmethod
    def list_backend_security_original_ids(backend_session: Session) -> List[str]:
        """
        Lists original ids from backend database
        Args:
            backend_session: Backend database session

        Returns: original ids
        """
        return [ value for value, in backend_session.query(destination_models.Security.original_id).all() ]

    @staticmethod
    def upsert_security(backend_session: Session, security, original_id, updated, fund_id=None, currency="", name_fi="",
                        name_sv="", name_en='', series_id=None) -> destination_models.Security:
        new_security = security if security else destination_models.Security()
        new_security.original_id = original_id
        new_security.fund_id = fund_id
        new_security.currency = currency
        new_security.name_fi = name_fi
        new_security.name_sv = name_sv
        new_security.name_en = name_en
        new_security.series_id = series_id
        new_security.updated = updated
        backend_session.add(new_security)
        return new_security


class MigrateSecurityRatesTask(AbstractFundsTask):
    """
    Migration task for security rates
    """

    def get_name(self):
        return "security-rates"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = backend_session.execute(statement="SELECT COUNT(ID) FROM security_rate").scalar()
            funds_count = funds_session.execute(statement="SELECT COUNT(*) FROM TABLE_RATE").scalar()
            return backend_count >= funds_count

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            last_funds_dates = None if force_recheck else self.get_last_funds_dates(funds_session=funds_session)
            last_backend_dates = None if force_recheck else self.get_last_backend_dates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if self.should_timeout(timeout=timeout):
                    break

                if not force_recheck:
                    last_fund_date = last_funds_dates.get(security.original_id, None)
                    if not last_fund_date:
                        continue

                    last_backend_date = last_backend_dates.get(security.id, date(1970, 1, 1))
                    if last_fund_date <= last_backend_date:
                        continue
                else:
                    last_backend_date = date(1970, 1, 1)

                synchronized_count += self.migrate_security_rates(security=security,
                                                                  backend_session=backend_session,
                                                                  funds_session=funds_session,
                                                                  last_backend_date=last_backend_date,
                                                                  timeout=timeout,
                                                                  force_recheck=force_recheck
                                                                  )

            if self.should_timeout(timeout=timeout):
                self.print_message(TIMED_OUT)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            funds_verification_values = self.get_funds_verification_values(funds_session=funds_session)
            backend_verification_values = self.get_backend_verification_values(backend_session=backend_session)
            result = True

            if funds_verification_values.count != backend_verification_values.count:
                self.print_message(f"Warning: Count mismatch {funds_verification_values.count} != "
                                   f"{backend_verification_values.count} in security_rate table")
                result = False

            if funds_verification_values.rate_close_sum != backend_verification_values.rate_close_sum:
                self.print_message(f"Warning: Rate close sum mismatch {funds_verification_values.rate_close_sum} != "
                                   f"{backend_verification_values.rate_close_sum} in security_rate table")
                result = False

            if not result:
                self.print_suggests(
                    backend_session=backend_session,
                    funds_session=funds_session
                )

            return result

    def print_suggests(self, backend_session: Session, funds_session: Session):
        """
        Prints suggested fix for verification issues

        Args:
            backend_session: Backend session
            funds_session: Funds session
        """
        securities = self.list_securities(backend_session=backend_session)
        for security in securities:
            funds_rate_rows = self.list_funds_security_rates(
                funds_session=funds_session,
                security=security,
                rdate=date(1970, 1, 1),
                offset=0,
                limit=100000
            )

            for funds_rate_row in funds_rate_rows:
                funds_rate_date = funds_rate_row.RDATE
                funds_rate_close = funds_rate_row.RCLOSE

                backend_security_rate = self.get_security_rate(
                    backend_session=backend_session,
                    security=security,
                    rate_date=funds_rate_date
                )

                sec_id = security.original_id

                if backend_security_rate is None:
                    self.print_message(f"Warning Rate close missing from {funds_rate_date} for {sec_id}")
                elif funds_rate_close != backend_security_rate.rate_close:
                    self.print_message(f"Suggest: UPDATE security_rate "
                                       f"SET rate_close = {funds_rate_close} "
                                       f"WHERE rate_date=DATE('{funds_rate_date}') AND "
                                       f"security_id=(SELECT id FROM security WHERE original_id = '{sec_id}')")

    @staticmethod
    def get_funds_verification_values(funds_session: Session):
        """
        Returns verification values for funds database.

        Args:
            funds_session: Session to funds database.

        Returns:
            Verification values.
        """
        return funds_session.execute("SELECT COUNT(*) as count, SUM(RCLOSE) as rate_close_sum FROM TABLE_RATE").one()

    @staticmethod
    def get_backend_verification_values(backend_session: Session):
        """
        Returns verification values for backend database.

        Args:
            backend_session: Session to backend database.

        Returns:
            Verification values.
        """
        return backend_session.execute("SELECT COUNT(id) as count, SUM(rate_close) as rate_close_sum "
                                       "FROM security_rate").one()

    def migrate_security_rates(self, security: destination_models.Security,
                               funds_session: Session,
                               backend_session: Session,
                               last_backend_date: date,
                               timeout: datetime,
                               force_recheck: bool
                               ) -> int:
        """
        Migrates security rates
        Args:
            security: security
            funds_session: fund database session
            backend_session: backend database session
            last_backend_date: last backend update date
            timeout: timeout
            force_recheck: whether this is a force recheck run

        Returns: synchronized count
        """
        batch = 1000
        offset = 0
        synchronized_count = 0

        while not self.should_timeout(timeout=timeout):
            self.print_message(f"Migrating security {security.original_id} rates from offset {offset}")

            rate_rows = self.list_funds_security_rates(
                funds_session=funds_session,
                security=security,
                rdate=last_backend_date,
                offset=offset,
                limit=batch
            )

            if rate_rows.rowcount == 0:
                break

            for rate_row in rate_rows:
                rate_date = rate_row.RDATE
                rate_close = rate_row.RCLOSE

                existing_security_rate = (offset == 0 or force_recheck) and self.get_security_rate(
                    backend_session=backend_session,
                    security=security,
                    rate_date=rate_date
                )

                if force_recheck or not existing_security_rate:
                    self.upsert_security_rate(
                        backend_session=backend_session,
                        existing_security_rate=existing_security_rate,
                        security=security,
                        rate_date=rate_date,
                        rate_close=rate_close
                    )

                    synchronized_count = synchronized_count + 1

            if rate_rows.rowcount != -1 and rate_rows.rowcount < batch:
                break

            offset += batch

        return synchronized_count

    @staticmethod
    def get_last_backend_dates(backend_session: Session) -> Dict[UUID, date]:
        """
        Returns dict of last security backend dates
        Args:
            backend_session: backend database session

        Returns: dict of last security backend dates"""
        result = {}
        rows = backend_session.query(destination_models.SecurityRate.security_id,
                                     func.max(destination_models.SecurityRate.rate_date)) \
            .group_by(destination_models.SecurityRate.security_id) \
            .all()

        for row in rows:
            result[row[0]] = row[1]

        return result

    @staticmethod
    def get_last_funds_dates(funds_session: Session) -> Dict[str, date]:
        """
        Returns dict of last security fund dates
        Args:
            funds_session: fund database session

        Returns: dict of last security fund dates
        """
        result = {}
        rows = funds_session.execute("SELECT SECID, max(RDATE) as LAST_DATE FROM TABLE_RATE GROUP BY SECID")
        for row in rows:
            result[row.SECID] = row.LAST_DATE.date()
        return result

    @staticmethod
    def list_funds_security_rates(funds_session: Session, security: destination_models.Security, rdate: date,
                            limit: int, offset: int):
        """
        Lists rates from funds database
        Args:
            funds_session: Funds database session
            rdate: min rdate
            security: security
            limit: max results
            offset: offset

        Returns: rates from funds database
        """
        return funds_session.execute('SELECT RDATE, RCLOSE FROM TABLE_RATE WHERE RDATE >= :rdate AND SECID = :SECID '
                                     'ORDER BY RDATE, SECID OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY',
                                     {
                                         "limit": limit,
                                         "offset": offset,
                                         "rdate": rdate.isoformat(),
                                         "SECID": security.original_id
                                     })

    @staticmethod
    def get_security_rate(backend_session: Session,
                          security: destination_models.Security,
                          rate_date: date
                          ) -> Optional[destination_models.SecurityRate]:
        """
        Returns whether rate exists for given security and date
        Args:
            backend_session: backend database session
            security: security
            rate_date: date

        Returns: whether rate exists for given security and date
        """
        return backend_session.query(destination_models.SecurityRate) \
                              .filter(and_(destination_models.SecurityRate.security_id == security.id,
                                           destination_models.SecurityRate.rate_date == rate_date)) \
                              .one_or_none()

    @staticmethod
    def upsert_security_rate(backend_session: Session,
                             security: destination_models.Security,
                             existing_security_rate: Optional[destination_models.SecurityRate],
                             rate_date: date,
                             rate_close: Decimal
                             ) -> destination_models.SecurityRate:
        """
        Inserts new row into security rate table
        Args:
            backend_session: backend database session
            existing_security_rate: existing security rate
            security: security
            rate_date: date
            rate_close: close
        """
        security_rate = existing_security_rate if existing_security_rate else destination_models.SecurityRate()
        security_rate.security = security
        security_rate.rate_date = rate_date
        security_rate.rate_close = rate_close
        backend_session.add(security_rate)
        return security_rate


class MigrateLastRatesTask(AbstractFundsTask):
    """
    Migration task for last rates
    """

    def __init__(self):
        self.backend_entities = None
        self.funds_entities = None

    def get_name(self):
        return "last-rate"

    def prepare(self, backend_session: Session):
        with Session(self.get_funds_database_engine()) as funds_session:
            fund_rows = funds_session.execute("SELECT SECID, RDATE, RCLOSE FROM TABLE_RATELAST")
            backend_rows = backend_session.query(destination_models.LastRate).all()
            self.funds_entities = {x.SECID: x for x in fund_rows}
            self.backend_entities = {x.security.original_id: x for x in backend_rows}

    def up_to_date(self, backend_session: Session) -> bool:
        for security_original_id, funds_row in self.funds_entities.items():
            existing_last_rate = self.backend_entities.get(security_original_id, None)
            if not existing_last_rate or not existing_last_rate.rate_date or \
                    existing_last_rate.rate_date < funds_row.RDATE.date():
                self.print_message(f"Security {security_original_id} last rate is not up-to-date")
                return False

        return True

    def verify(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            funds_verification_values = self.get_funds_verification_values(funds_session=funds_session)
            backend_verification_values = self.get_backend_verification_values(backend_session=backend_session)

            if funds_verification_values.count != backend_verification_values.count:
                self.print_message(f"Warning: Count mismatch {funds_verification_values.count} != "
                                   f"{backend_verification_values.count} in last_rate table")
                return False

            if funds_verification_values.rate_close_sum != backend_verification_values.rate_close_sum:
                self.print_message(f"Warning: Rate close sum mismatch {funds_verification_values.rate_close_sum} != "
                                   f"{backend_verification_values.rate_close_sum} in last_rate table")
                return False

            return True

    @staticmethod
    def get_funds_verification_values(funds_session: Session):
        """
        Returns verification values for funds database.

        Args:
            funds_session: Session to funds database.

        Returns:
            Verification values.
        """
        return funds_session.execute("SELECT COUNT(*) as count, SUM(RCLOSE) as rate_close_sum FROM TABLE_RATELAST")\
            .one()

    @staticmethod
    def get_backend_verification_values(backend_session: Session):
        """
        Returns verification values for backend database.

        Args:
            backend_session: Session to backend database.

        Returns:
            Verification values.
        """
        return backend_session.execute("SELECT COUNT(id) as count, SUM(rate_close) as rate_close_sum "
                                       "FROM last_rate").one()

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0

        for security_original_id, funds_row in self.funds_entities.items():
            existing_last_rate = self.backend_entities.get(security_original_id, None)
            funds_rate_date = funds_row.RDATE.date()
            rate_date = existing_last_rate.rate_date if existing_last_rate else None

            if rate_date is None:
                rate_date = date(1970, 1, 1)

            if rate_date < funds_rate_date:
                self.print_message(f"Updating security {security_original_id} last rate "
                                   f"({rate_date} < {funds_rate_date})")

                security = self.get_security_by_original_id(backend_session=backend_session,
                                                            original_id=funds_row.SECID)
                if not security:
                    raise MissingSecurityException(
                        original_id=funds_row.SECID
                    )

                self.upsert_last_rate(backend_session=backend_session,
                                      last_rate=existing_last_rate,
                                      security_id=security.id,
                                      rate_close=funds_row.RCLOSE,
                                      rate_date=funds_row.RDATE
                                      )
                synchronized_count = synchronized_count + 1

        return synchronized_count

    @staticmethod
    def upsert_last_rate(backend_session: Session,
                         last_rate: Optional[destination_models.LastRate],
                         security_id: UUID,
                         rate_close: Decimal,
                         rate_date: date) -> destination_models.LastRate:
        """
        Upserts last rate entity
        Args:
            backend_session: database session for the backend database
            last_rate: last rate table or null if creating new one
            security_id: security id
            rate_close: rate close
            rate_date: rate date

        Returns: updated last rate entity
        """
        new_last_rate = last_rate if last_rate else destination_models.LastRate()
        new_last_rate.security_id = security_id
        new_last_rate.rate_close = rate_close
        new_last_rate.rate_date = rate_date
        backend_session.add(new_last_rate)
        return new_last_rate


class MigrateCompaniesTask(AbstractFundsTask):
    """
    Migration task for companies
    """

    def __init__(self):
        """
        Constructor
        """
        self.source_updated = None
        self.backend_updated = datetime(1970, 1, 1, 0, 0)

    def get_name(self):
        return "companies"

    def prepare(self, backend_session: Session):
        """
        Resolves last update dates for both databases

        Args:
            backend_session: backend database session
        """
        with Session(self.get_funds_database_engine()) as funds_session:
            self.source_updated = self.get_source_last_update_date(funds_session=funds_session)
            self.backend_updated = self.get_backend_last_update_date(backend_session=backend_session)

            if self.source_updated is None:
                self.source_updated = datetime(1970, 1, 1, 0, 0)

            self.source_updated = self.round_datetime_to_seconds(self.source_updated)
            self.backend_updated = self.round_datetime_to_seconds(self.backend_updated)

    def up_to_date(self, backend_session: Session) -> bool:
        if self.backend_updated != self.source_updated:
            return False

        with Session(self.get_funds_database_engine()) as funds_session:
            funds_count = self.count_funds_companies(funds_session=funds_session)
            backend_count = self.count_backend_companies(backend_session=backend_session)
            return funds_count == backend_count

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0
        batch = 10000
        offset = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            self.print_message(f"Updating companies, source updated: {self.source_updated}, "
                               f"backend_updated: {self.backend_updated}")

            funds_company_com_codes = []
            backend_companies = list(self.list_backend_companies(backend_session=backend_session))
            backend_company_map = {x.original_id: x for x in backend_companies}

            while not self.should_timeout(timeout=timeout):
                self.print_message(f"Migrating companies from offset {offset}")

                funds_company_rows = self.list_funds_companies(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if funds_company_rows.rowcount == 0:
                    break

                for funds_company_row in funds_company_rows:
                    com_code = funds_company_row.COM_CODE
                    name = funds_company_row.NAME1
                    so_sec_nr = funds_company_row.SO_SEC_NR
                    created = funds_company_row.CREA_DATE
                    updated = funds_company_row.UPD_DATE

                    funds_company_com_codes.append(com_code)

                    if not updated or created > updated:
                        updated = created

                    if not updated:
                        updated = datetime(1970, 1, 1, 0, 0)

                    existing_company = backend_company_map.get(com_code, None)
                    self.upsert_company(
                        backend_session=backend_session,
                        original_id=com_code,
                        name=name,
                        existing_company=existing_company,
                        updated=updated,
                        ssn=so_sec_nr
                    )

                    synchronized_count = synchronized_count + 1

                offset += batch

            backend_original_ids = backend_company_map.keys()
            removed_com_codes = []

            for original_id in backend_original_ids:
                if original_id not in funds_company_com_codes:
                    removed_com_codes.append(original_id)

            if len(removed_com_codes) > 0:
                removed_company_ids_query = backend_session.query(destination_models.Company.id) \
                    .filter(destination_models.Company.original_id.in_(removed_com_codes))

                removed_company_ids = [value for value, in removed_company_ids_query]

                log_c_company_ids = backend_session.query(destination_models.PortfolioLog.c_company_id) \
                    .filter(destination_models.PortfolioLog.c_company_id.in_(removed_company_ids))

                company_access_company_ids = backend_session.query(destination_models.CompanyAccess.company_id) \
                    .filter(destination_models.CompanyAccess.company_id.in_(removed_company_ids))

                portfolio_company_ids = backend_session.query(destination_models.Portfolio.company_id) \
                    .filter(destination_models.Portfolio.company_id.in_(removed_company_ids))

                company_ids_in_use_rows = portfolio_company_ids.union(log_c_company_ids, company_access_company_ids)\
                    .all()

                company_ids_in_use = [value for value, in company_ids_in_use_rows]

                if len(company_ids_in_use) > 0:
                    self.print_message(f"Excluding companies in use from the removal {company_ids_in_use}")
                    removed_company_ids = set(removed_company_ids).difference(set(company_ids_in_use))

                if len(removed_company_ids) > 0:
                    self.print_message(f"Deleting {len(removed_company_ids)} companies")

                    synchronized_count = synchronized_count + backend_session.query(destination_models.Company) \
                        .filter(destination_models.Company.id.in_(removed_company_ids)) \
                        .delete(synchronize_session=False)

            if self.should_timeout(timeout=timeout):
                self.print_message(TIMED_OUT)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        batch = 10000
        offset = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            funds_company_count = self.count_funds_companies(funds_session=funds_session)
            backend_companies = list(self.list_backend_companies(backend_session=backend_session))

            if len(backend_companies) != funds_company_count:
                self.print_message(f"Warning: Companies count: {funds_company_count} != {len(backend_companies)} ")
                return False

            backend_company_map = {x.original_id: x for x in backend_companies}

            while offset < funds_company_count:
                funds_companies = self.list_funds_companies(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if funds_companies.rowcount == 0:
                    break

                for funds_company in funds_companies:
                    com_code = funds_company.COM_CODE
                    name = funds_company.NAME1
                    so_sec_nr = funds_company.SO_SEC_NR

                    if com_code not in backend_company_map:
                        self.print_message(f"Warning: Company {com_code} not found in backend")
                        return False

                    if backend_company_map[com_code].name != name:
                        self.print_message(f"Warning: Company {com_code} name mismatch "
                                           f"{backend_company_map[com_code].name} != {name}")
                        return False

                    if backend_company_map[com_code].ssn != so_sec_nr:
                        self.print_message(f"Warning: Company {com_code} ssn mismatch "
                                           f"{backend_company_map[com_code].ssn} != {so_sec_nr}")
                        return False

                self.print_message(f"Verified {offset}/{funds_company_count} companies")
                offset += batch

            self.print_message(f"Verified all companies")

        return True

    def get_source_last_update_date(self, funds_session: Session) -> datetime:
        """
        get last update date of company table from funds database
        Args:
            funds_session: Funds database session

        Returns: date from funds database
        """
        excluded = self.get_excluded_com_codes_query()
        statement = "SELECT MAX(UD) FROM (" \
                    f"SELECT MAX(CREA_DATE) AS UD FROM COMPANY WHERE COM_CODE NOT IN ({excluded})" \
                    "UNION " \
                    f"SELECT MAX(UPD_DATE) AS UD FROM COMPANY WHERE COM_CODE NOT IN ({excluded})" \
                    ") as U"
        return funds_session.execute(statement=statement).scalar()

    @staticmethod
    def get_backend_last_update_date(backend_session: Session) -> Optional[datetime]:
        """
        get last update date of company table from backend database
        Args:
            backend_session: Backend database session

        Returns: date from backend database
        """
        return backend_session.query(func.max(destination_models.Company.updated).label("last_update")).scalar()

    def list_funds_companies(self,
                             funds_session: Session,
                             limit: int,
                             offset: int
                             ):
        """
        Lists companies from funds database
        Args:
            funds_session: Funds database session
            limit: max results
            offset: offset

        Returns: companies from funds database
        """
        excluded = self.get_excluded_com_codes_query()
        return funds_session.execute(
            f"SELECT COM_CODE, NAME1, SO_SEC_NR, CREA_DATE, UPD_DATE FROM TABLE_COMPANY "
            f"WHERE COM_TYPE = '3' AND COM_CODE NOT IN ({excluded}) "
            "ORDER BY UPD_DATE, CREA_DATE OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY",
            {
                "limit": limit,
                "offset": offset
            })

    def count_funds_companies(self, funds_session: Session):
        """
        Count companies from funds database
        Args:
            funds_session: Funds database session

        Returns: count of companies from funds database
        """
        excluded = self.get_excluded_com_codes_query()
        return funds_session.execute(f"SELECT COUNT(COM_CODE) FROM TABLE_COMPANY "
                                     f"WHERE COM_TYPE = '3' AND COM_CODE NOT IN ({excluded})").scalar()

    @staticmethod
    def count_backend_companies(backend_session: Session):
        """
        Count companies from backend database
        Args:
            backend_session: Backend database session

        Returns: count of companies from backend database
        """
        return backend_session.query(func.count(destination_models.Company.id)).scalar()

    @staticmethod
    def get_excluded_com_codes_query() -> str:
        """
        Returns SQL query for excluded com codes
        Returns: SQL query for excluded com codes
        """
        return "SELECT DISTINCT P.COM_CODE FROM TABLE_PORTFOL P " \
               "INNER JOIN TABLE_PORCLASSDEF D ON P.COM_CODE = D.COM_CODE AND P.PORID = D.PORID " \
               "AND D.PORCLASS in(3, 4, 5) " \
               "AND P.COM_CODE NOT IN (" \
               "SELECT DISTINCT P.COM_CODE FROM TABLE_PORTFOL P " \
               "LEFT JOIN TABLE_PORCLASSDEF D ON " \
               "P.COM_CODE = D.COM_CODE AND P.PORID = D.PORID " \
               "WHERE D.PORCLASS IS NULL " \
               "UNION " \
               "SELECT DISTINCT P.COM_CODE " \
               "FROM TABLE_PORTFOL P " \
               "INNER JOIN TABLE_PORCLASSDEF D ON P.COM_CODE = D.COM_CODE " \
               "AND P.PORID = D.PORID AND D.PORCLASS in(1, 2))"

    @staticmethod
    def upsert_company(backend_session: Session,
                       original_id: str,
                       name: str,
                       existing_company: Optional[destination_models.Company],
                       updated: datetime,
                       ssn: str) -> destination_models.Company:
        """
        Inserts new company
        Args:
            backend_session: backend database session
            name: name of company
            original_id: original id
            existing_company: existing company
            updated: last update time
            ssn: ssn

        Returns: created company
        """
        new_company = existing_company if existing_company else destination_models.Company()
        new_company.original_id = original_id
        new_company.name = name
        new_company.ssn = ssn
        new_company.updated = updated
        backend_session.add(new_company)
        return new_company


class MigratePortfoliosTask(AbstractFundsTask):
    """
    Migration task for portfolios
    """

    def get_name(self):
        return "portfolios"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = self.count_backend_portfolios(backend_session=backend_session)
            funds_count = self.count_funds_portfolios(funds_session=funds_session)
            return backend_count == funds_count

    @staticmethod
    def count_backend_portfolios(backend_session: Session):
        """
        Counts backend database portfolios
        Args:
            backend_session: backend database session

        Returns: backend database portfolio count

        """
        return backend_session.query(func.count(destination_models.Portfolio.id)).scalar()

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0
        batch = 10000
        offset = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            funds_por_ids = []
            backend_portfolios = list(self.list_backend_portfolios(backend_session=backend_session))
            backend_portfolio_map = {x.original_id: x for x in backend_portfolios}
            backend_companies = list(self.list_backend_companies(backend_session=backend_session))
            backend_company_map = {x.original_id: x for x in backend_companies}

            while not self.should_timeout(timeout=timeout):
                self.print_message(f"Migrating portfolios from offset {offset}")

                funds_portfolio_rows = self.list_funds_portfolios(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if funds_portfolio_rows.rowcount == 0:
                    break

                for funds_portfolio_row in funds_portfolio_rows:
                    por_id = funds_portfolio_row.PORID
                    name = funds_portfolio_row.NAME1
                    com_code = funds_portfolio_row.COM_CODE
                    funds_por_ids.append(por_id)

                    company = backend_company_map.get(com_code, None)
                    if not company:
                        raise MissingCompanyException(
                            original_id=com_code
                        )

                    existing_portfolio = backend_portfolio_map.get(por_id, None)

                    self.upsert_portfolio(
                        backend_session=backend_session,
                        existing_portfolio=existing_portfolio,
                        original_id=por_id,
                        name=name,
                        company_id=company.id
                    )

                    synchronized_count = synchronized_count + 1

                offset += batch

            backend_original_ids = backend_portfolio_map.keys()
            removed_por_ids = []

            for original_id in backend_original_ids:
                if original_id not in funds_por_ids:
                    removed_por_ids.append(original_id)

            if len(removed_por_ids) > 0:
                removed_portfolio_ids_query = backend_session.query(destination_models.Portfolio.id) \
                    .filter(destination_models.Portfolio.original_id.in_(removed_por_ids))

                removed_portfolio_ids = [value for value, in removed_portfolio_ids_query]

                transactions_portfolio_ids = backend_session.query(destination_models.
                                                                   PortfolioTransaction.portfolio_id) \
                    .filter(destination_models.PortfolioTransaction.portfolio_id.in_(removed_portfolio_ids))

                log_portfolio_ids = backend_session.query(destination_models.PortfolioLog.portfolio_id) \
                    .filter(destination_models.PortfolioLog.portfolio_id.in_(removed_portfolio_ids))

                portfolio_ids_in_use_rows = transactions_portfolio_ids.union(log_portfolio_ids) \
                    .all()

                portfolio_ids_in_use = [value for value, in portfolio_ids_in_use_rows]

                if len(portfolio_ids_in_use) > 0:
                    self.print_message(f"Excluding portfolios in use from the removal {portfolio_ids_in_use}")
                    removed_portfolio_ids = set(removed_portfolio_ids).difference(set(portfolio_ids_in_use))

                if len(removed_portfolio_ids) > 0:
                    self.print_message(f"Deleting portfolios with original_ids {removed_portfolio_ids}")
                    
                    synchronized_count = synchronized_count + backend_session.query(destination_models.Portfolio) \
                        .filter(destination_models.Portfolio.id.in_(removed_portfolio_ids)) \
                        .delete(synchronize_session=False)

            if self.should_timeout(timeout=timeout):
                self.print_message(TIMED_OUT)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        batch = 10000
        offset = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            funds_portfolio_count = self.count_funds_portfolios(funds_session=funds_session)
            backend_portfolios = list(self.list_backend_portfolios(backend_session=backend_session))
            backend_companies = list(self.list_backend_companies(backend_session=backend_session))
            backend_company_map = {x.id: x for x in backend_companies}

            if len(backend_portfolios) != funds_portfolio_count:
                self.print_message(f"Warning: Portfolios count: {funds_portfolio_count} != {len(backend_portfolios)} ")
                return False

            backend_portfolio_map = {x.original_id: x for x in backend_portfolios}

            while offset < funds_portfolio_count:
                funds_portfolios = self.list_funds_portfolios(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if funds_portfolios.rowcount == 0:
                    break

                for funds_portfolio in funds_portfolios:
                    por_id = funds_portfolio.PORID
                    name = funds_portfolio.NAME1
                    com_code = funds_portfolio.COM_CODE

                    if por_id not in backend_portfolio_map:
                        self.print_message(f"Warning: Portfolio {por_id} not found in backend")
                        return False

                    if backend_portfolio_map[por_id].name != name:
                        self.print_message(f"Warning: Portfolio {por_id} name mismatch "
                                           f"{backend_portfolio_map[por_id].name} != {name}")
                        return False

                    backend_portfolio_id = backend_portfolio_map[por_id].company_id
                    backend_company = backend_company_map.get(backend_portfolio_id, None)
                    if backend_company is None:
                        self.print_message(f"Warning: Portfolio {por_id} company not found in backend")
                        return False

                    if backend_company.original_id != com_code:
                        self.print_message(f"Warning: Portfolio {por_id} company_id mismatch "
                                           f"{backend_company.original_id} != {com_code}")
                        return False

                self.print_message(f"Verified {offset}/{funds_portfolio_count} portfolios")
                offset += batch

            self.print_message(f"Verified all portfolios")

        return True

    def count_funds_portfolios(self, funds_session: Session):
        """
        Counts portfolios from funds database
        Args:
            funds_session: Funds database session

        Returns: count of portfolios from funds database
        """
        exclude_query = self.get_excluded_portfolio_ids_query()
        return funds_session.execute('SELECT COUNT(PORID) FROM TABLE_PORTFOL '
                                     f'WHERE PORID NOT IN ({exclude_query})') \
            .scalar()

    @staticmethod
    def list_backend_portfolios(backend_session: Session):
        """
        Lists portfolios from backend database
        Args:
            backend_session: Backend database session

        Returns: portfolios from backend database
        """
        return backend_session.query(destination_models.Portfolio).all()

    def list_funds_portfolios(self, funds_session: Session, limit: int, offset: int):
        """
        Lists portfolios from funds database
        Args:
            funds_session: Funds database session
            limit: max results
            offset: offset

        Returns: portfolios from funds database
        """
        exclude_query = self.get_excluded_portfolio_ids_query()
        return funds_session.execute('SELECT PORID, NAME1, COM_CODE FROM TABLE_PORTFOL '
                                     f'WHERE PORID NOT IN ({exclude_query})'
                                     'ORDER BY PORID OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY',
                                     {
                                         "limit": limit,
                                         "offset": offset
                                     })

    @staticmethod
    def upsert_portfolio(backend_session: Session,
                         existing_portfolio: Optional[destination_models.Portfolio],
                         original_id: str,
                         name: str,
                         company_id: UUID
                         ) -> destination_models.Portfolio:
        """
        Creates new portfolio
        Args:
            backend_session: backend database session
            existing_portfolio: existing portfolio
            original_id: original id
            company_id: company id
            name: name

        Returns: created portfolio
        """
        new_portfolio = existing_portfolio if existing_portfolio else destination_models.Portfolio()
        new_portfolio.original_id = original_id
        new_portfolio.company_id = company_id
        new_portfolio.name = name
        backend_session.add(new_portfolio)
        return new_portfolio


class MigratePortfolioLogsTask(AbstractFundsTask):
    """
    Migration task for portfolio logs
    """

    def get_name(self):
        return "portfolio-logs"

    def up_to_date(self, backend_session: Session) -> bool:
        return False

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0
        batch = 20000
        unix_time = datetime(1970, 1, 1, 0, 0)
        selected_security = self.options.get('security', None)
        backend_companies = list(self.list_backend_companies(backend_session=backend_session))
        backend_company_map = {x.original_id: x for x in backend_companies}

        with Session(self.get_funds_database_engine()) as funds_session:

            funds_updates = self.get_funds_updates(funds_session=funds_session)
            backend_updates = self.get_backend_updates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if selected_security is not None and security.original_id != selected_security:
                    continue

                if self.should_timeout(timeout=timeout):
                    break

                offset = 0

                if force_recheck:
                    backend_update = datetime(1970, 1, 1)
                else:
                    funds_updated = funds_updates.get(security.original_id, None)
                    if not funds_updated:
                        continue

                    backend_update = backend_updates.get(security.id, None)
                    if not backend_update:
                        backend_update = datetime(1970, 1, 1)

                    if funds_updated <= backend_update:
                        continue

                    self.print_message(f"Security {security.original_id} portfolio logs are not upd-to-date funds "
                                       f"{funds_updated}, backend {backend_update}")

                while not self.should_timeout(timeout=timeout):
                    self.print_message(f"Migrating security {security.original_id} portfolio logs from offset {offset}")

                    portfolio_log_rows = list(self.list_portfolio_logs(
                        funds_session=funds_session,
                        security=security,
                        updated=backend_update,
                        offset=offset,
                        limit=batch
                    ).fetchall())

                    if len(portfolio_log_rows) == 0:
                        break

                    trans_nrs = list(map(lambda i: i.TRANS_NR, portfolio_log_rows))
                    por_ids = set(map(lambda i: i.PORID, portfolio_log_rows))

                    existing_portfolio_logs = backend_session.query(destination_models.PortfolioLog).filter(
                        destination_models.PortfolioLog.transaction_number.in_(trans_nrs)) \
                        .all()

                    portfolio_ids = backend_session.query(destination_models.Portfolio.id,
                                                          destination_models.Portfolio.original_id) \
                        .filter(destination_models.Portfolio.original_id.in_(por_ids)).all()

                    existing_portfolio_log_map = {x.transaction_number: x for x in existing_portfolio_logs}
                    portfolio_id_map = {x.original_id: x.id for x in portfolio_ids}

                    for portfolio_log_row in portfolio_log_rows:
                        c_security_original_id = portfolio_log_row.CSECID
                        # for the case that null is inserted as SECID = ' '
                        if c_security_original_id and c_security_original_id.strip():
                            c_security = self.get_security_by_original_id(backend_session=backend_session,
                                                                          original_id=c_security_original_id)
                            if not c_security:
                                raise MissingSecurityException(
                                    original_id=c_security_original_id
                                )

                            c_security_id = c_security.id
                        else:
                            c_security_id = None

                        portfolio_original_id = portfolio_log_row.PORID
                        if portfolio_original_id:
                            portfolio_id = portfolio_id_map.get(portfolio_original_id, None)
                            if not portfolio_id:
                                raise MissingPortfolioException(
                                    original_id=portfolio_original_id
                                )

                        else:
                            # without the portfolio key we cant do anything, we try to grab the right portfolio from
                            # portfolio table considering the company code. If there are more than one portfolio then
                            # we should alert and ask how to resolve the situation manually.
                            company = backend_company_map.get(portfolio_log_row.COM_CODE, None)
                            if not company:
                                raise MissingCompanyException(
                                    original_id=portfolio_log_row.COM_CODE
                                )

                            portfolios = self.list_portfolios_by_company(backend_session=backend_session,
                                                                         company_id=company.id)
                            if len(portfolios) != 1:
                                raise MigrationException(f"Could not resolve portfolio for company "
                                                         f"{portfolio_log_row.COM_CODE}")

                            else:
                                portfolio = portfolios[0]
                                portfolio_id = portfolio.id

                        ccom_code = portfolio_log_row.CCOM_CODE
                        if ccom_code and ccom_code.strip() != '':
                            c_company = backend_company_map.get(ccom_code, None)
                            if not c_company:
                                raise MissingCompanyException(
                                    original_id=ccom_code
                                )
                            c_company_id = c_company.id
                        else:
                            c_company_id = None

                        existing_portfolio_log = existing_portfolio_log_map.get(portfolio_log_row.TRANS_NR, None)
                        logged_date = portfolio_log_row.PMT_DATE

                        # dates that are before 1970-01-01 are considered to be nulls
                        if logged_date and logged_date > unix_time:
                            payment_date = logged_date
                        else:
                            payment_date = None

                        self.upsert_portfolio_log(session=backend_session,
                                                  portfolio_log=existing_portfolio_log,
                                                  transaction_number=portfolio_log_row.TRANS_NR,
                                                  transaction_code=portfolio_log_row.TRANS_CODE,
                                                  transaction_date=portfolio_log_row.TRANS_DATE,
                                                  c_total_value=portfolio_log_row.CTOT_VALUE,
                                                  portfolio_id=portfolio_id,
                                                  security_id=security.id,
                                                  c_security_id=c_security_id,
                                                  c_company_id=c_company_id,
                                                  amount=portfolio_log_row.AMOUNT,
                                                  c_price=portfolio_log_row.CPRICE,
                                                  payment_date=payment_date,
                                                  c_value=portfolio_log_row.CVALUE,
                                                  provision=portfolio_log_row.PROVISION,
                                                  status=portfolio_log_row.STATUS,
                                                  updated=portfolio_log_row.UPDATED)

                        synchronized_count = synchronized_count + 1

                    if len(portfolio_log_rows) < batch:
                        break

                    offset += batch

            if self.should_timeout(timeout=timeout):
                self.print_message(TIMED_OUT)

            return synchronized_count

    def get_funds_verification_values(self, funds_session: Session, secid: str):
        """
        Returns verification values for funds database.

        Args:
            funds_session: Session to funds database.
            secid: Security id.

        Returns:
            Verification values.
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        selects = ",".join([
            "SUM(CAST(TRANS_CODE as BIGINT)) as trans_code_sum",
            "SUM(CAST(TRANS_NR as BIGINT)) as trans_nr_sum",
            "SUM(CAST(CTOT_VALUE as decimal(15,2))) as ctot_value_sum",
            "SUM(CAST(AMOUNT as decimal(19,6))) as amount_sum",
            "SUM(CAST(CVALUE as decimal(15,2))) as cvalue_sum",
            "SUM(CAST(CPRICE as decimal(19,6))) as cprice_sum",
            "SUM(CAST(PROVISION as decimal(15,2))) as provision_sum",
            "SUM(CAST(status as BIGINT)) as status_sum",
            "SUM(COALESCE(CAST(DATEDIFF(MINUTE, '1970-01-01', PMT_DATE) as BIGINT), 0)) as pmt_date_sum",
            "SUM(COALESCE(CAST(DATEDIFF(MINUTE, '1970-01-01', TRANS_DATE) as BIGINT), 0)) as trans_date_date_sum",
            "SUM(CAST(REPLACE(CASE PORID WHEN '' THEN COM_CODE ELSE PORID END, '_', '.') "
            "   as DECIMAL(38, 2))) as por_id_sum",
            "SUM(CAST(REPLACE(TRIM(CCOM_CODE),'', 0) as BIGINT)) as ccom_code_sum"
        ])

        return funds_session.execute(f"SELECT {selects} FROM TABLE_PORTLOG "
                                     f"WHERE PORID NOT IN ({porid_exclude_query}) AND SECID = :secid",
                                     {
                                         "secid": secid
                                     }).one()

    @staticmethod
    def get_backend_verification_values(backend_session: Session, security_id: UUID):
        """
        Returns verification values for backend database.

        Args:
            backend_session: Session to backend database.
            security_id: Security id.

        Returns:
            Verification values.
        """

        pmt_date_sum = func.sum(func.coalesce(func.cast(
            func.TIMESTAMPDIFF(text('MINUTE'), datetime(1970, 1, 1), destination_models.PortfolioLog.payment_date),
            Integer), 0))

        trans_date_date_sum = func.sum(func.coalesce(func.cast(
            func.TIMESTAMPDIFF(text('MINUTE'), datetime(1970, 1, 1), destination_models.PortfolioLog.transaction_date),
            Integer), 0))

        portfolio_original_id_query = backend_session.query(destination_models.Portfolio.original_id)\
            .filter(destination_models.Portfolio.id == destination_models.PortfolioLog.portfolio_id).scalar_subquery()

        por_id_sum = func.sum(
            func.cast(func.replace(portfolio_original_id_query, '_', '.'), DECIMAL(38, 2))
        )

        c_company_query = backend_session.query(destination_models.Company.original_id)\
            .filter(destination_models.Company.id == destination_models.PortfolioLog.c_company_id)\
            .scalar_subquery()

        query = backend_session.query(
            func.sum(destination_models.PortfolioLog.transaction_code).label("trans_code_sum"),
            func.sum(destination_models.PortfolioLog.transaction_number).label("trans_nr_sum"),
            func.sum(destination_models.PortfolioLog.c_total_value).label("ctot_value_sum"),
            func.sum(destination_models.PortfolioLog.amount).label("amount_sum"),
            func.sum(destination_models.PortfolioLog.c_value).label("cvalue_sum"),
            func.sum(destination_models.PortfolioLog.c_price).label("cprice_sum"),
            func.sum(destination_models.PortfolioLog.provision).label("provision_sum"),
            func.sum(destination_models.PortfolioLog.status).label("status_sum"),
            pmt_date_sum.label("pmt_date_sum"),
            trans_date_date_sum.label("trans_date_date_sum"),
            por_id_sum.label("por_id_sum"),
            func.sum(c_company_query).label("ccom_code_sum")
        ).filter(destination_models.PortfolioLog.security_id == security_id)

        return query.one()

    def get_funds_csec_counts(self, funds_session: Session, secid: str):
        """
        Returns ccec counts for given secid
        Args:
            funds_session: Session to funds database.
            secid: Security id.
        Returns:
            csec counts
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        return funds_session.execute(f"SELECT CSECID, count(CSECID) as count FROM TABLE_PORTLOG "
                                     f"WHERE CSECID IS NOT NULL AND CSECID != '' AND "
                                     f"PORID NOT IN ({porid_exclude_query}) AND SECID = :secid "
                                     f"GROUP BY CSECID;",
                                     {
                                         "secid": secid
                                     }).all()

    @staticmethod
    def get_backend_c_security_counts(backend_session: Session, security_id: UUID):
        """
        Returns csec counts for given secid
        Args:
            backend_session: Session to backend database.
            security_id: Security id.

        Returns:
            csec counts
        """
        c_security_original_id_query = backend_session.query(destination_models.Security.original_id)\
            .filter(destination_models.Security.id == destination_models.PortfolioLog.c_security_id).scalar_subquery()

        query = backend_session.query(
            c_security_original_id_query.label("CSECID"),
            func.count(destination_models.PortfolioLog.c_security_id).label("count"))\
            .filter(destination_models.PortfolioLog.security_id == security_id)\
            .filter(destination_models.PortfolioLog.c_security_id.isnot(None))\
            .group_by(destination_models.PortfolioLog.c_security_id)

        return query.all()

    def verify(self, backend_session: Session) -> bool:
        selected_security = self.options.get('security', None)
        result = True

        with Session(self.get_funds_database_engine()) as funds_session:
            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if selected_security is not None and security.original_id != selected_security:
                    continue

                security_valid = True

                self.print_message(f"Verifying security {security.original_id} portfolio logs")

                funds_row_count = self.count_funds_portfolio_logs(
                    funds_session=funds_session,
                    secid=security.original_id
                )

                backend_row_count = self.count_backend_portfolio_logs(
                    backend_session=backend_session,
                    security_id=security.id
                )

                if funds_row_count != backend_row_count:
                    security_valid = False
                elif funds_row_count > 0:
                    backend_verification_values = self.get_backend_verification_values(
                        backend_session=backend_session,
                        security_id=security.id
                    )

                    funds_verification_values = self.get_funds_verification_values(
                        funds_session=funds_session,
                        secid=security.original_id
                    )

                    backend_c_security_counts = self.get_backend_c_security_counts(
                        backend_session=backend_session,
                        security_id=security.id
                    )

                    backend_c_security_counts_map = {x.CSECID: x.count for x in backend_c_security_counts}

                    funds_c_security_counts = self.get_funds_csec_counts(
                        funds_session=funds_session,
                        secid=security.original_id
                    )

                    for funds_c_security_count in funds_c_security_counts:
                        cssecid = funds_c_security_count.CSECID
                        count = funds_c_security_count.count

                        if cssecid not in backend_c_security_counts_map:
                            self.print_message(f"Warning: c_security {cssecid}"
                                               f" not found in portfolio logs in security"
                                               f" {security.original_id}. ")
                            security_valid = False
                        elif backend_c_security_counts_map[cssecid] != count:
                            self.print_message(f"Warning: c_security {cssecid} count mismatch"
                                               f" in security {security.original_id}. "
                                               f" {backend_c_security_counts_map[cssecid]}, != {count}")
                            security_valid = False

                    if funds_verification_values.trans_code_sum != backend_verification_values.trans_code_sum:
                        self.print_message(f"Warning: Transaction code sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.trans_code_sum} != "
                                           f"{funds_verification_values.trans_code_sum}")
                        security_valid = False

                    if funds_verification_values.trans_nr_sum != backend_verification_values.trans_nr_sum:
                        self.print_message(f"Warning: Transaction number sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.trans_nr_sum} != "
                                           f"{funds_verification_values.trans_nr_sum}")
                        security_valid = False

                    if funds_verification_values.ctot_value_sum != backend_verification_values.ctot_value_sum:
                        self.print_message(f"Warning: Total value sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.ctot_value_sum} != "
                                           f"{funds_verification_values.ctot_value_sum}")
                        security_valid = False

                    if funds_verification_values.amount_sum != backend_verification_values.amount_sum:
                        self.print_message(f"Warning: Amount sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.amount_sum} != "
                                           f"{funds_verification_values.amount_sum}")
                        security_valid = False

                    if funds_verification_values.cvalue_sum != backend_verification_values.cvalue_sum:
                        self.print_message(f"Warning: C value sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.cvalue_sum} != "
                                           f"{funds_verification_values.cvalue_sum}")
                        security_valid = False

                    if funds_verification_values.cprice_sum != backend_verification_values.cprice_sum:
                        self.print_message(f"Warning: C pricew sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.cprice_sum} != "
                                           f"{funds_verification_values.cprice_sum}")
                        security_valid = False

                    if funds_verification_values.pmt_date_sum != backend_verification_values.pmt_date_sum:
                        self.print_message(f"Warning: payment date sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.pmt_date_sum} != "
                                           f"{funds_verification_values.pmt_date_sum}")
                        security_valid = False

                    if funds_verification_values.trans_date_date_sum != backend_verification_values.trans_date_date_sum:
                        self.print_message(f"Warning: transaction date sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.trans_date_date_sum} != "
                                           f"{funds_verification_values.trans_date_date_sum}")
                        security_valid = False

                    if funds_verification_values.por_id_sum != backend_verification_values.por_id_sum:
                        self.print_message(f"Warning: portfolio id sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.por_id_sum} != "
                                           f"{funds_verification_values.por_id_sum}")
                        security_valid = False

                    if funds_verification_values.ccom_code_sum != backend_verification_values.ccom_code_sum:
                        self.print_message(f"Warning: c company id sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.ccom_code_sum} != "
                                           f"{funds_verification_values.ccom_code_sum}")
                        security_valid = False

                    if funds_verification_values.status_sum != backend_verification_values.status_sum:
                        self.print_message(f"Warning: status sum mismatch in portfolio logs in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.status_sum} != "
                                           f"{funds_verification_values.status_sum}")

                        security_valid = False

                if not security_valid:
                    funds_nrs = self.list_funds_portfolio_log_trans_nrs(
                        funds_session=funds_session,
                        secid=security.original_id
                    )

                    backend_transaction_numbers = self.list_backend_portfolio_log_transaction_numbers(
                        backend_session=backend_session,
                        security_id=security.id
                    )

                    missing_transaction_numbers = set(funds_nrs).difference(set(backend_transaction_numbers))
                    extra_transaction_numbers = set(backend_transaction_numbers).difference(set(funds_nrs))

                    if len(missing_transaction_numbers) > 0:
                        self.print_message(f"Warning: Missing transaction numbers: {missing_transaction_numbers}")

                        for missing_transaction_number in missing_transaction_numbers:
                            self.print_suggested_insert(
                                trans_nr=missing_transaction_number,
                                backend_session=backend_session,
                                funds_session=funds_session
                            )

                    if len(extra_transaction_numbers) > 0:
                        self.print_message(f"Warning: Extra transaction numbers: {extra_transaction_numbers}")

                    self.print_suggested_status_updates(
                        funds_session=funds_session,
                        backend_session=backend_session,
                        security=security
                    )

                result = security_valid and result

            return result

    def print_suggested_status_updates(self,
                                       funds_session: Session,
                                       backend_session: Session,
                                       security: destination_models.Security
                                       ):
        """
        Prints the suggested status updates for the given security.
        Args:
            funds_session: The funds database session.
            backend_session: The backend database session.
            security: The security to print the status updates for.
        """
        fund_statuses = list(self.list_fund_statuses(
            funds_session=funds_session,
            security=security,
            updated=datetime(1970, 1, 1)
        ).fetchall())

        backend_status = self.list_backend_statuses(
            backend_session=backend_session,
            security_id=security.id
        )

        backend_status_map = {x.transaction_number: x for x in backend_status}

        for fund_status in fund_statuses:
            backend_status = backend_status_map.get(fund_status.TRANS_NR, None)
            if backend_status and fund_status.STATUS != backend_status.status:
                self.print_message(f"Suggest: UPDATE portfolio_log SET status = {fund_status.STATUS} "
                                   f"WHERE transaction_number = {fund_status.TRANS_NR};")

    def print_suggested_insert(self, trans_nr: str, funds_session: Session, backend_session: Session):
        """
        Prints suggested fix for detected fault

        Args:
            funds_session: Funds database session
            trans_nr: transaction number
        """
        fund_portlog = self.find_fund_portfolio_log(funds_session=funds_session, trans_nr=trans_nr)
        if not fund_portlog:
            self.print_message(f"Warning: could not find missing portfolio log with transaction number {trans_nr}")
        else:
            por_id = fund_portlog.PORID.strip() if fund_portlog.PORID else None
            com_code = fund_portlog.COM_CODE.strip() if fund_portlog.COM_CODE else None

            if por_id:
                portfolio_select = f"(SELECT id FROM portfolio WHERE original_id = '{por_id}')"
            else:
                company = self.get_company_by_original_id(backend_session=backend_session, original_id=com_code)
                if not company:
                    self.print_message(f"Warning: could not find company by com code {com_code} "
                                       f"for missing transaction {trans_nr}")

                portfolios = self.list_portfolios_by_company(backend_session=backend_session,
                                                             company_id=company.id)
                if len(portfolios) != 1:
                    self.print_message(f"Warning: could not resolve portfolio for company by com code {com_code} "
                                       f"for missing transaction {trans_nr}")
                    return

                else:
                    portfolio_select = f"(SELECT id FROM portfolio WHERE original_id = '{portfolios[0].original_id}')"

            values = ",".join([
                "(UNHEX(REPLACE(UUID(), '-', '')))",
                str(fund_portlog.TRANS_NR),
                f"'{fund_portlog.TRANS_CODE}'",
                f"DATE('{fund_portlog.TRANS_DATE.isoformat()}')" if fund_portlog.TRANS_DATE else "NULL",
                f"{fund_portlog.CTOT_VALUE}",
                portfolio_select,
                f"(SELECT id FROM security WHERE original_id = '{fund_portlog.SECID}')" if
                fund_portlog.SECID and fund_portlog.SECID.strip() else "NULL",

                f"(SELECT id FROM security WHERE original_id = '{fund_portlog.CSECID}')" if
                fund_portlog.CSECID and fund_portlog.CSECID.strip() else "NULL",

                f"{fund_portlog.AMOUNT}",
                f"{fund_portlog.CPRICE}",
                f"DATE('{fund_portlog.PMT_DATE.isoformat()}')" if fund_portlog.PMT_DATE else "NULL",
                f"{fund_portlog.CVALUE}",
                f"{fund_portlog.PROVISION}",
                f"'{fund_portlog.STATUS}'",
                f"DATE('{fund_portlog.UPDATED.isoformat()}')" if fund_portlog.UPDATED else "NULL"
            ])

            self.print_message(f"Suggest: INSERT INTO portfolio_log (`id`, `transaction_number`, "
                               f"`transaction_code`, `transaction_date`, `c_total_value`, `portfolio_id`, "
                               f"`security_id`, `c_security_id`, `amount`, `c_price`, `payment_date`, `c_value`, "
                               f"`provision`, `status`, `updated`) VALUES ({values});")

    def count_funds_portfolio_logs(self, funds_session: Session, secid: str):
        """
        Count portfolio logs from funds database
        Args:
            funds_session: Funds database session
            secid: security id

        Returns: Number of portfolio logs
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        return funds_session.execute(
            f"SELECT COUNT(TRANS_NR) FROM TABLE_PORTLOG "
            f"WHERE PORID NOT IN ({porid_exclude_query}) AND SECID = :secid", {
                "secid": secid
            }).scalar()

    @staticmethod
    def count_backend_portfolio_logs(backend_session: Session, security_id: UUID):
        """
        Count portfolio logs from backend database
        Args:
            backend_session: Backend database session
            security_id: Security id

        Returns: count of portfolio logs from backend database
        """
        return backend_session.query(func.count(destination_models.PortfolioLog.id))\
            .filter(destination_models.PortfolioLog.security_id == security_id)\
            .scalar()

    def list_funds_portfolio_log_trans_nrs(self, funds_session: Session, secid: str):
        """
        Lists portfolio log trans nrs from funds database
        Args:
            funds_session: Funds database session
            secid: security id

        Returns: portfolio log nrs
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        rows = funds_session.execute(f"SELECT TRANS_NR FROM TABLE_PORTLOG " 
                                     f"WHERE PORID NOT IN ({porid_exclude_query}) AND SECID = :secid",
                                     {
                                         "secid": secid
                                     }).all()

        return [value for value, in rows]

    @staticmethod
    def list_backend_portfolio_log_transaction_numbers(backend_session: Session, security_id: UUID):
        """
        List log transaction numbers from backend database
        Args:
            backend_session: Backend database session
            security_id: Security id

        Returns: portfolio log transaction numbers
        """
        rows = backend_session.query(destination_models.PortfolioLog.transaction_number)\
            .filter(destination_models.PortfolioLog.security_id == security_id)\
            .all()

        return [value for value, in rows]

    @staticmethod
    def get_backend_updates(backend_session: Session) -> Dict[UUID, datetime]:
        """
        Returns dict of updated values from backend database
        Args:
            backend_session: backend database session

        Returns: dict of updated values from backend database"""
        result = {}
        rows = backend_session.query(destination_models.PortfolioLog.security_id,
                                     func.max(destination_models.PortfolioLog.updated)) \
            .group_by(destination_models.PortfolioLog.security_id) \
            .all()

        for row in rows:
            result[row[0]] = row[1]

        return result

    @staticmethod
    def get_funds_updates(funds_session: Session) -> Dict[str, datetime]:
        """
        Returns dict of updated values from funds database
        Args:
            funds_session: fund database session

        Returns: dict of updated values from funds database
        """
        result = {}
        rows = funds_session.execute(
            "SELECT SECID, max(UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME)) as LAST_DATE "
            "FROM TABLE_PORTLOG GROUP BY SECID")
        for row in rows:
            result[row.SECID] = row.LAST_DATE
        return result

    def list_portfolio_logs(self, funds_session: Session, security: destination_models.Security, updated: datetime,
                            limit: int, offset: int):
        """
        Lists rates from funds database
        Args:
            funds_session: Funds database session
            updated: min updated
            security: security
            limit: max results
            offset: offset

        Returns: rates from funds database
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        return funds_session.execute("SELECT SECID, CSECID, PORID, COM_CODE, TRANS_NR, TRANS_CODE, TRANS_DATE, "
                                     "CCOM_CODE, CTOT_VALUE, AMOUNT, CPRICE, PMT_DATE, CVALUE, PROVISION, STATUS, "
                                     "UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) as UPDATED "
                                     "FROM TABLE_PORTLOG "
                                     "WHERE UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) >= :updated AND "
                                     "SECID = :secid AND "
                                     "PORID IN (SELECT PORID FROM TABLE_PORTFOL) AND "
                                     f"PORID NOT IN ({porid_exclude_query}) "
                                     "ORDER BY UPDATED, SECID OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;",
                                     {
                                         "limit": limit,
                                         "offset": offset,
                                         "updated": updated.isoformat(),
                                         "secid": security.original_id
                                     })

    def list_fund_statuses(self, funds_session: Session, security: destination_models.Security, updated: datetime):
        """
        Lists statuses from funds database
        Args:
            funds_session: Funds database session
            updated: min updated
            security: security

        Returns: statuses from funds database
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        return funds_session.execute("SELECT TRANS_NR, STATUS "
                                     "FROM TABLE_PORTLOG "
                                     "WHERE UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) >= :updated AND "
                                     "SECID = :secid AND "
                                     "PORID IN (SELECT PORID FROM TABLE_PORTFOL) AND "
                                     f"PORID NOT IN ({porid_exclude_query}) ",
                                     {
                                         "updated": updated.isoformat(),
                                         "secid": security.original_id
                                     })

    @staticmethod
    def list_backend_statuses(backend_session: Session, security_id: UUID):
        """
        List statuses from backend database
        Args:
            backend_session: Backend database session
            security_id: Security id

        Returns: statuses from backend database
        """
        return backend_session.query(destination_models.PortfolioLog.transaction_number,
                                     destination_models.PortfolioLog.status)\
            .filter(destination_models.PortfolioLog.security_id == security_id)\
            .all()

    @staticmethod
    def find_fund_portfolio_log(funds_session: Session, trans_nr: str):
        """
        Lists rates from funds database
        Args:
            funds_session: Funds database session
            trans_nr: transaction number

        Returns: found portfolio log or None if not found
        """
        return funds_session.execute("SELECT SECID, CSECID, PORID, COM_CODE, TRANS_NR, TRANS_CODE, TRANS_DATE, "
                                     "CTOT_VALUE, AMOUNT, CPRICE, PMT_DATE, CVALUE, PROVISION, STATUS, "
                                     "UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) as UPDATED "
                                     "FROM TABLE_PORTLOG "
                                     "WHERE TRANS_NR = :trans_nr",
                                     {
                                         "trans_nr": trans_nr
                                     }).one_or_none()

    @staticmethod
    def upsert_portfolio_log(session,
                             portfolio_log,
                             transaction_number,
                             transaction_code,
                             transaction_date,
                             c_total_value,
                             portfolio_id,
                             security_id,
                             c_security_id,
                             c_company_id: Optional[UUID],
                             amount: Decimal,
                             c_price: Decimal,
                             payment_date,
                             c_value,
                             provision,
                             status,
                             updated: datetime
                             ):
        new_portfolio_log = portfolio_log if portfolio_log else destination_models.PortfolioLog()
        new_portfolio_log.transaction_number = transaction_number
        new_portfolio_log.transaction_code = transaction_code
        new_portfolio_log.transaction_date = transaction_date
        new_portfolio_log.c_total_value = c_total_value
        new_portfolio_log.portfolio_id = portfolio_id
        new_portfolio_log.security_id = security_id
        new_portfolio_log.c_security_id = c_security_id
        new_portfolio_log.c_company_id = c_company_id
        new_portfolio_log.amount = amount
        new_portfolio_log.c_price = c_price
        new_portfolio_log.payment_date = payment_date
        new_portfolio_log.c_value = c_value
        new_portfolio_log.provision = provision
        new_portfolio_log.status = status
        new_portfolio_log.updated = updated
        session.add(new_portfolio_log)
        return new_portfolio_log


class MigratePortfolioTransactionsTask(AbstractFundsTask):
    """
    Migration task for portfolio transactions
    """

    def get_name(self):
        return "portfolio-transactions"

    def up_to_date(self, backend_session: Session) -> bool:
        return False

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0
        batch = 1000

        with Session(self.get_funds_database_engine()) as funds_session:

            funds_updates = self.get_funds_updates(funds_session=funds_session)
            backend_updates = self.get_backend_updates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if self.should_timeout(timeout=timeout):
                    break

                self.print_message(f"Checking removed portfolio transactions from security {security.original_id}...")

                funds_nrs = self.list_funds_portfolio_transaction_trans_nrs(
                    funds_session=funds_session,
                    secid=security.original_id
                )

                backend_transaction_numbers = self.list_backend_portfolio_transaction_transaction_numbers(
                    backend_session=backend_session,
                    security_id=security.id
                )

                removed_trans_nrs = set(backend_transaction_numbers).difference(set(funds_nrs))

                if len(removed_trans_nrs) > 0:
                    removed_count = backend_session.query(destination_models.PortfolioTransaction) \
                        .filter(destination_models.PortfolioTransaction.transaction_number.in_(removed_trans_nrs)) \
                        .delete(synchronize_session=False)

                    if removed_count > 0:
                        self.print_message(f"Removed {removed_count} portfolio transactions.")
                        synchronized_count += removed_count

                offset = 0

                funds_updated = funds_updates.get(security.original_id, None)
                if not funds_updated:
                    continue

                if force_recheck:
                    backend_update = datetime(1970, 1, 1)
                else:
                    backend_update = backend_updates.get(security.id, None)
                    if not backend_update:
                        backend_update = datetime(1970, 1, 1)

                if funds_updated <= backend_update:
                    continue

                self.print_message(f"Security {security.original_id} portfolio transactions are not upd-to-date funds "
                                   f"{funds_updated}, backend {backend_update}")

                while not self.should_timeout(timeout=timeout):
                    self.print_message(f"Migrating security {security.original_id} portfolio transactions "
                                       f"from offset {offset}")

                    portfolio_transaction_cursor = self.list_portfolio_transactions(
                        funds_session=funds_session,
                        security=security,
                        updated=backend_update,
                        offset=offset,
                        limit=batch
                    )

                    if portfolio_transaction_cursor.rowcount == 0:
                        break

                    portfolio_transaction_rows = list(portfolio_transaction_cursor.fetchall())
                    trans_nrs = list(map(lambda i: i.TRANS_NR, portfolio_transaction_rows))
                    por_ids = set(map(lambda i: i.PORID, portfolio_transaction_rows))

                    existing_transactions = backend_session.query(destination_models.PortfolioTransaction) \
                        .filter(destination_models.PortfolioTransaction.transaction_number.in_(trans_nrs)) \
                        .all()

                    portfolio_ids = backend_session.query(destination_models.Portfolio.id,
                                                          destination_models.Portfolio.original_id) \
                        .filter(destination_models.Portfolio.original_id.in_(por_ids)).all()

                    existing_transaction_map = {x.transaction_number: x for x in existing_transactions}
                    portfolio_id_map = {x.original_id: x.id for x in portfolio_ids}

                    for portfolio_transaction_row in portfolio_transaction_rows:
                        portfolio_original_id = portfolio_transaction_row.PORID
                        portfolio_id = portfolio_id_map.get(portfolio_original_id, None)
                        if not portfolio_id:
                            raise MissingPortfolioException(
                                original_id=portfolio_original_id
                            )

                        existing_transaction = existing_transaction_map.get(portfolio_transaction_row.TRANS_NR, None)

                        self.upsert_portfolio_transaction(backend_session=backend_session,
                                                          portfolio_transaction=existing_transaction,
                                                          transaction_number=portfolio_transaction_row.TRANS_NR,
                                                          transaction_date=portfolio_transaction_row.TRANS_DATE,
                                                          amount=portfolio_transaction_row.AMOUNT,
                                                          purchase_c_value=portfolio_transaction_row.PUR_CVALUE,
                                                          portfolio_id=portfolio_id,
                                                          security_id=security.id,
                                                          updated=portfolio_transaction_row.UPDATED
                                                          )

                        synchronized_count = synchronized_count + 1

                    if len(portfolio_transaction_rows) < batch:
                        break

                    offset += batch

            if self.should_timeout(timeout=timeout):
                self.print_message(TIMED_OUT)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        selected_security = self.options.get('security', None)
        result = True

        with Session(self.get_funds_database_engine()) as funds_session:
            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if selected_security is not None and security.original_id != selected_security:
                    continue

                security_valid = True

                self.print_message(f"Verifying security {security.original_id} portfolio transactions")

                backend_verification_values = self.get_backend_verification_values(
                    backend_session=backend_session,
                    security_id=security.id
                )

                funds_verification_values = self.get_funds_verification_values(
                    funds_session=funds_session,
                    secid=security.original_id
                )

                if funds_verification_values.count != backend_verification_values.count:
                    self.print_message(f"Warning: Transaction row count mismatch in portfolio transaction in security"
                                       f" {security.original_id}. "
                                       f"{backend_verification_values.count} != "
                                       f"{funds_verification_values.count}")
                    security_valid = False
                else:
                    if funds_verification_values.trans_nr_sum != backend_verification_values.trans_nr_sum:
                        self.print_message(f"Warning: Transaction number sum mismatch in "
                                           f"portfolio transaction in security "
                                           f"{security.original_id}. "
                                           f"{backend_verification_values.trans_nr_sum} != "
                                           f"{funds_verification_values.trans_nr_sum}")
                        security_valid = False

                    if funds_verification_values.amount_sum != backend_verification_values.amount_sum:
                        self.print_message(f"Warning: Amount sum mismatch in portfolio transaction in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.amount_sum} != "
                                           f"{funds_verification_values.amount_sum}")
                        security_valid = False

                    if funds_verification_values.purc_value_sum != backend_verification_values.purc_value_sum:
                        self.print_message(f"Warning: purchase C value sum mismatch in portfolio transaction in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.purc_value_sum} != "
                                           f"{funds_verification_values.purc_value_sum}")
                        security_valid = False

                    if funds_verification_values.por_id_sum != backend_verification_values.por_id_sum:
                        self.print_message(f"Warning: portfolio id sum mismatch in portfolio transaction in security"
                                           f" {security.original_id}. "
                                           f"{backend_verification_values.por_id_sum} != "
                                           f"{funds_verification_values.por_id_sum}")
                        security_valid = False

                if not security_valid:
                    funds_nrs = self.list_funds_portfolio_transaction_trans_nrs(
                        funds_session=funds_session,
                        secid=security.original_id
                    )

                    backend_transaction_numbers = self.list_backend_portfolio_transaction_transaction_numbers(
                        backend_session=backend_session,
                        security_id=security.id
                    )

                    missing_transaction_numbers = set(funds_nrs).difference(set(backend_transaction_numbers))
                    extra_transaction_numbers = set(backend_transaction_numbers).difference(set(funds_nrs))

                    self.print_message(f"Missing transaction numbers: {missing_transaction_numbers}")
                    self.print_message(f"Extra transaction numbers: {extra_transaction_numbers}")

                    for missing_transaction_number in missing_transaction_numbers:
                        self.print_suggested_insert(
                            trans_nr=missing_transaction_number,
                            funds_session=funds_session
                        )

                    for extra_transaction_number in extra_transaction_numbers:
                        self.print_suggested_delete(
                            trans_nr=extra_transaction_number
                        )

                result = result and security_valid

            return result

    def print_suggested_insert(self, funds_session: Session, trans_nr: str):
        """
        Prints suggested fix for detected fault

        Args:
            funds_session: Funds database session
            trans_nr: transaction number
        """
        fund_portrans = self.find_fund_porttrans(funds_session=funds_session, trans_nr=trans_nr)
        if not fund_portrans:
            self.print_message(f"Warning: could not find missing portfolio transaction "
                               f"with transaction number {trans_nr}")
        else:
            columns = ",".join([
                "`id`",
                "`portfolio_id`",
                "`security_id`",
                "`transaction_number`",
                "`transaction_date`",
                "`amount`",
                "`purchase_c_value`",
                "`updated`"
            ])

            values = ",".join([
                "(UNHEX(REPLACE(UUID(), '-', '')))",
                f"(SELECT id FROM portfolio WHERE original_id = '{fund_portrans.PORID}')",
                f"(SELECT id FROM security WHERE original_id = '{fund_portrans.SECID}')",
                str(fund_portrans.TRANS_NR),
                f"DATE('{fund_portrans.TRANS_DATE.isoformat()}')" if fund_portrans.TRANS_DATE else "NULL",
                f"{fund_portrans.AMOUNT}",
                f"{fund_portrans.PUR_CVALUE}",
                f"DATE('{fund_portrans.UPDATED.isoformat()}')" if fund_portrans.UPDATED else "NULL"
            ])

            self.print_message(f"Suggest: INSERT INTO portfolio_transaction ({columns}) VALUES ({values});")

    def print_suggested_delete(self, trans_nr: str):
        """
        Prints suggested fix for detected fault

        Args:
            trans_nr: transaction number
        """
        self.print_message(f"Suggest: DELETE FROM portfolio_transaction WHERE transaction_number = {trans_nr};")

    def get_funds_verification_values(self, funds_session: Session, secid: str):
        """
        Returns verification values for funds database.

        Args:
            funds_session: Session to funds database.
            secid: Security id.

        Returns:
            Verification values.
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        selects = ",".join([
            "COUNT(TRANS_NR) as count",
            "SUM(CAST(TRANS_NR as BIGINT)) as trans_nr_sum",
            "SUM(CAST(AMOUNT as decimal(19,6))) as amount_sum",
            "SUM(CAST(PUR_CVALUE as decimal(15,2))) as purc_value_sum",
            "SUM(CAST(REPLACE(PORID, '_', '.') as DECIMAL(38, 2))) as por_id_sum"
        ])

        return funds_session.execute(f"SELECT {selects} FROM TABLE_PORTRANS "
                                     f"WHERE PORID NOT IN ({porid_exclude_query}) AND SECID = :secid",
                                     {
                                         "secid": secid
                                     }).one()

    @staticmethod
    def get_backend_verification_values(backend_session: Session, security_id: UUID):
        """
        Returns verification values for backend database.

        Args:
            backend_session: Session to backend database.
            security_id: Security id.

        Returns:
            Verification values.
        """

        portfolio_original_id_query = backend_session.query(destination_models.Portfolio.original_id)\
            .filter(destination_models.Portfolio.id == destination_models.PortfolioTransaction.portfolio_id)\
            .scalar_subquery()

        por_id_sum = func.sum(
            func.cast(func.replace(portfolio_original_id_query, '_', '.'), DECIMAL(38, 2))
        )

        return backend_session.query(
            func.count(destination_models.PortfolioTransaction.transaction_number).label("count"),
            func.sum(destination_models.PortfolioTransaction.transaction_number).label("trans_nr_sum"),
            func.sum(destination_models.PortfolioTransaction.amount).label("amount_sum"),
            func.sum(destination_models.PortfolioTransaction.purchase_c_value).label("purc_value_sum"),
            por_id_sum.label("por_id_sum")
        ).filter(destination_models.PortfolioTransaction.security_id == security_id).one()

    @staticmethod
    def get_backend_updates(backend_session: Session) -> Dict[UUID, datetime]:
        """
        Returns dict of updated values from backend database
        Args:
            backend_session: backend database session

        Returns: dict of updated values from backend database"""
        result = {}
        rows = backend_session.query(destination_models.PortfolioTransaction.security_id,
                                     func.max(destination_models.PortfolioTransaction.updated)) \
            .group_by(destination_models.PortfolioTransaction.security_id) \
            .all()

        for row in rows:
            result[row[0]] = row[1]

        return result

    def get_funds_updates(self, funds_session: Session) -> Dict[str, datetime]:
        """
        Returns dict of updated values from funds database
        Args:
            funds_session: fund database session

        Returns: dict of updated values from funds database
        """
        result = {}
        excluded = self.get_excluded_portfolio_ids_query()
        rows = funds_session.execute(
            "SELECT SECID, max(UPD_DATE + CAST(UPD_TIME as DATETIME)) as LAST_DATE "
            f"FROM TABLE_PORTRANS WHERE PORID NOT IN ({excluded}) GROUP BY SECID")
        for row in rows:
            result[row.SECID] = row.LAST_DATE
        return result

    def list_portfolio_transactions(self, funds_session: Session, security: destination_models.Security,
                                    updated: datetime, limit: int, offset: int):
        """
        Lists portfolio transactions from funds database
        Args:
            funds_session: Funds database session
            updated: min updated
            security: security
            limit: max results
            offset: offset

        Returns: portfolio transactions from funds database
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()
        return funds_session.execute("SELECT PORID, COM_CODE, TRANS_NR, TRANS_DATE, AMOUNT, PUR_CVALUE, "
                                     "UPD_DATE + CAST(UPD_TIME as DATETIME) as UPDATED "
                                     "FROM TABLE_PORTRANS "
                                     "WHERE UPD_DATE + CAST(UPD_TIME as DATETIME) >= :updated AND "
                                     "SECID = :secid AND "
                                     f"PORID NOT IN ({porid_exclude_query}) "
                                     "ORDER BY UPDATED, SECID OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;",
                                     {
                                         "limit": limit,
                                         "offset": offset,
                                         "updated": updated.isoformat(),
                                         "secid": security.original_id
                                     })

    @staticmethod
    def find_fund_porttrans(funds_session: Session, trans_nr: str):
        """
        Lists portfolio transactions from funds database
        Args:
            funds_session: Funds database session
            trans_nr: trans nr

        Returns: found portfolio transaction or None if not found
        """
        return funds_session.execute("SELECT PORID, SECID, TRANS_NR, TRANS_DATE, AMOUNT, PUR_CVALUE, "
                                     "UPD_DATE + CAST(UPD_TIME as DATETIME) as UPDATED "
                                     "FROM TABLE_PORTRANS "
                                     "WHERE TRANS_NR = :trans_nr",
                                     {
                                         "trans_nr": trans_nr
                                     }).one_or_none()

    def list_funds_portfolio_transaction_trans_nrs(self, funds_session: Session, secid: str):
        """
        Lists portfolio transaction trans nrs from funds database
        Args:
            funds_session: Funds database session
            secid: security id

        Returns: portfolio transaction nrs
        """
        porid_exclude_query = self.get_excluded_portfolio_ids_query()

        rows = funds_session.execute(f"SELECT TRANS_NR FROM TABLE_PORTRANS " 
                                     f"WHERE PORID NOT IN ({porid_exclude_query}) AND SECID = :secid",
                                     {
                                         "secid": secid
                                     }).all()

        return [value for value, in rows]

    @staticmethod
    def list_backend_portfolio_transaction_transaction_numbers(backend_session: Session, security_id: UUID):
        """
        List log transaction numbers from backend database
        Args:
            backend_session: Backend database session
            security_id: Security id

        Returns: portfolio log transaction numbers
        """
        rows = backend_session.query(destination_models.PortfolioTransaction.transaction_number)\
            .filter(destination_models.PortfolioTransaction.security_id == security_id)\
            .all()

        return [value for value, in rows]

    @staticmethod
    def upsert_portfolio_transaction(backend_session: Session,
                                     portfolio_transaction: destination_models.PortfolioTransaction,
                                     transaction_number: int,
                                     transaction_date: date,
                                     amount: Decimal,
                                     purchase_c_value: Decimal,
                                     portfolio_id: UUID,
                                     security_id: UUID,
                                     updated: datetime):
        """
        Upserts portfolio transaction
        Args:
            backend_session: backend database session
            portfolio_transaction: portfolio transaction
            transaction_number: transaction number
            transaction_date: transaction date
            amount: amount
            purchase_c_value: purchase c value
            portfolio_id: portfolio id
            security_id: security id
            updated: updated time

        Returns: created / updated entry
        """
        new_port_trans = portfolio_transaction if portfolio_transaction else destination_models.PortfolioTransaction()
        new_port_trans.transaction_number = transaction_number
        new_port_trans.transaction_date = transaction_date
        new_port_trans.amount = amount
        new_port_trans.purchase_c_value = purchase_c_value
        new_port_trans.portfolio_id = portfolio_id
        new_port_trans.security_id = security_id
        new_port_trans.updated = updated
        backend_session.add(new_port_trans)
        return new_port_trans


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
        return False

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0

        with Session(self.kiid_engine) as kiid_session:
            fund_rows = self.list_fund_rows(kiid_session=kiid_session)
            kiid_ids = []

            for fund_row in fund_rows:
                fund_id = fund_row.ID
                kiid_ids.append(fund_id)

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

                if fund_row.VOLATILITY_CAT:
                    fund.risk_level = fund_row.VOLATILITY_CAT

                if fund_row.FUND_TYPE:
                    fund.group = self.get_fund_group(fund_type=fund_row.FUND_TYPE)

                fund.deprecated = fund_row.DEPRECATED == 1

                backend_session.add(fund)
                synchronized_count = synchronized_count + 1

            backend_original_ids = self.list_original_ids_backend(backend_session=backend_session)
            removed_original_ids = []
            for original_id in backend_original_ids:
                if original_id not in kiid_ids:
                    removed_original_ids.append(original_id)

            if len(removed_original_ids) > 0:
                self.print_message(f"Deleting funds with original_ids {removed_original_ids}")

                synchronized_count = synchronized_count + backend_session.query(destination_models.Fund) \
                    .filter(destination_models.Fund.original_id.in_(removed_original_ids)) \
                    .delete(synchronize_session=False)

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        with Session(self.kiid_engine) as kiid_session:
            kiid_funds = self.list_fund_rows(kiid_session=kiid_session).all()
            backend_funds = self.list_backend_funds(backend_session=backend_session)
            backend_fund_map = {x.original_id: x for x in backend_funds}

            if len(backend_funds) != len(kiid_funds):
                self.print_message(f"Warning: Fund count mismatch: "
                                   f"{len(backend_funds)} != {len(kiid_funds)} ")
                return False

            for kiid_fund in kiid_funds:
                if kiid_fund.ID not in backend_fund_map:
                    self.print_message(f"Warning: Fund {kiid_fund.ID} not found in backend")
                    return False

                backend_fund = backend_fund_map[kiid_fund.ID]
                fund_group = self.get_fund_group(fund_type=kiid_fund.FUND_TYPE)
                fund_risk_level = str(kiid_fund.VOLATILITY_CAT) if kiid_fund.VOLATILITY_CAT else None

                if fund_group != backend_fund.group:
                    self.print_message(f"Warning: Fund group for fund {kiid_fund.ID}"
                                       f" {fund_group} != {backend_fund.group}")
                    return False

                if fund_risk_level != backend_fund.risk_level:
                    self.print_message(f"Warning: Fund risk_level for fund {kiid_fund.ID}"
                                       f" {kiid_fund.VOLATILITY_CAT} != {backend_fund.risk_level}")
                    return False

                if kiid_fund.URL_FI != backend_fund.kiid_url_fi:
                    self.print_message(f"Warning: Fund kiid_url_fi for fund {kiid_fund.ID}"
                                       f" {kiid_fund.URL_FI} != {backend_fund.kiid_url_fi}")
                    return False

                if kiid_fund.URL_EN != backend_fund.kiid_url_en:
                    self.print_message(f"Warning: Fund kiid_url_sv for fund {kiid_fund.ID}"
                                       f" {kiid_fund.URL_EN} != {backend_fund.kiid_url_en}")
                    return False

                if kiid_fund.URL_SV != backend_fund.kiid_url_sv:
                    self.print_message(f"Warning: Fund kiid_url_fi for fund {kiid_fund.ID}"
                                       f" {kiid_fund.URL_SV} != {backend_fund.kiid_url_sv}")
                    return False

                if kiid_fund.DEPRECATED == 1 != backend_fund.deprecated:
                    self.print_message(f"Warning: Fund deprecated for fund {kiid_fund.ID}"
                                       f" {kiid_fund.DEPRECATED == 1} != {backend_fund.deprecated}")
                    return False

            self.print_message(f"Verified all funds")

        return True

    @staticmethod
    def list_original_ids_backend(backend_session: Session) -> List[str]:
        """
        Lists original ids from backend database
        Args:
            backend_session: Backend database session

        Returns: original ids
        """
        return [ value for value, in backend_session.query(destination_models.Fund.original_id).all() ]

    @staticmethod
    def count_rows_kiid(kiid_session: Session):
        """
        Counts funds from KIID database
        Args:
            kiid_session: KIID database session

        Returns: count from funds database
        """
        statement = "SELECT COUNT(ID) FROM FUND"
        return kiid_session.execute(statement=statement).scalar()

    @staticmethod
    def count_rows_backend(backend_session: Session):
        """
        Counts funds from backend database
        Args:
            backend_session: Backend database session

        Returns: count from backend database
        """
        return backend_session.execute(statement="SELECT COUNT(id) FROM fund").scalar()

    @staticmethod
    def list_fund_rows(kiid_session: Session):
        """
        Lists rows from the kiid funds table
        Args:
            kiid_session: KIID database session

        Returns: rows from the kiid funds table
        """
        statement = f"SELECT ID, URL_FI, URL_SV, URL_EN, VOLATILITY_CAT, FUND_TYPE, DEPRECATED FROM FUND"
        return kiid_session.execute(statement=statement)

    @staticmethod
    def list_backend_funds(backend_session: Session) -> List[destination_models.Fund]:
        """
        Lists funds from backend database
        Args:
            backend_session: Backend database session

        Returns: funds
        """
        return backend_session.query(destination_models.Fund).all()

    @staticmethod
    def get_fund_group(fund_type: str) -> str:
        """
        Returns fund group from fund type
        Args:
            fund_type: fund type

        Returns:
            fund group
        """
        fund_group = re.sub(r'(?=[A-Z])', '_', fund_type).upper()
        if fund_group in FUND_GROUPS:
            return fund_group
        else:
            raise MigrationException(f"Could not recognize fund type ${fund_type}")

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


class MigrateCompanyAccessTask(AbstractSalkkuTask):
    """
    Migration task for company access
    """

    def get_name(self):
        return "company_access"

    def up_to_date(self, backend_session: Session) -> bool:
        return False

    def migrate(self, backend_session: Session, timeout: datetime, force_recheck: bool) -> int:
        synchronized_count = 0

        companies = list(backend_session.query(destination_models.Company.id,
                                               destination_models.Company.original_id
                                               ).all()
                         )

        company_original_id_map = {x.original_id: x for x in companies}
        company_id_map = {x.id: x for x in companies}

        existing_rows = self.list_backend_company_access(backend_session=backend_session)
        existing_map = {}

        for existing_row in existing_rows:
            company = company_id_map[existing_row.company_id]
            key = f"{existing_row.ssn}-{company.original_id}"
            existing_map[key] = existing_row

        with Session(self.get_salkku_database_engine()) as salkku_session:
            self.print_message(f"Migrating company access")
            authorization_rows = self.list_salkku_authorizations(salkku_session=salkku_session)
            deleted_keys = list(existing_map.keys())
            added_authorizations = []

            for authorization_row in authorization_rows:
                key = f"{authorization_row.authorizedSSN}-{authorization_row.comCode}"
                if key not in existing_map:
                    added_authorizations.append(authorization_row)
                else:
                    deleted_keys.remove(key)

            for deleted_key in deleted_keys:
                deleted_row = existing_map[deleted_key]

                backend_session.query(destination_models.CompanyAccess) \
                    .filter(destination_models.CompanyAccess.company_id == deleted_row.company_id) \
                    .filter(destination_models.CompanyAccess.ssn == deleted_row.ssn) \
                    .delete(synchronize_session=False)

                synchronized_count = synchronized_count + 1

            for added_authorization in added_authorizations:
                ssn = added_authorization.authorizedSSN
                com_code = added_authorization.comCode
                company = company_original_id_map.get(str(com_code), None)
                if not company:
                    self.print_message(f"Warning Company {com_code} not found")
                else:
                    self.insert_company_access(
                        backend_session=backend_session,
                        company=company,
                        ssn=ssn
                    )

                synchronized_count = synchronized_count + 1

            return synchronized_count

    def verify(self, backend_session: Session) -> bool:
        with Session(self.get_salkku_database_engine()) as salkku_session:
            salkku_company_accesses = self.list_salkku_authorizations(salkku_session=salkku_session).all()
            salkku_company_accesses_map = {f"{x.authorizedSSN}-{x.comCode}": x for x in salkku_company_accesses}
            backend_company_accesses = self.list_backend_company_access(backend_session=backend_session)

            if len(backend_company_accesses) != len(salkku_company_accesses):
                self.print_message(f"Warning: Company access count mismatch: "
                                   f"{len(backend_company_accesses)} != {len(salkku_company_accesses)} ")
                return False

            for backend_company_access in backend_company_accesses:
                backend_company = backend_company_access.company
                key = f"{backend_company_access.ssn}-{backend_company.original_id}"

                if key not in salkku_company_accesses_map:
                    self.print_message(f"Warning: Company access with key {key} not found in backend")
                    return False

            self.print_message(f"Verified all company accesses")

        return True

    @staticmethod
    def list_salkku_authorizations(salkku_session: Session):
        """
        Lists authorizations from salkku database

        Args:
            salkku_session: salkku database

        Returns:
            List of authorizations from salkku database
        """
        return salkku_session.execute('SELECT '
                                      '  authorizedSSN, comCode '
                                      'FROM  '
                                      '  Authorization '
                                      'WHERE '
                                      '  os_deny = 0 AND '
                                      '  validity = 1 AND '
                                      '  (expires IS NULL OR expires >= CURDATE()) '
                                      'GROUP BY '
                                      '  authorizedSSN, comCode')

    @staticmethod
    def list_backend_company_access(backend_session: Session):
        """
        Lists company access from backend database
        Args:
            backend_session: backend database

        Returns:
            List of company access from backend database
        """
        return backend_session.query(destination_models.CompanyAccess).all()

    @staticmethod
    def insert_company_access(backend_session: Session,
                              company: destination_models.Company,
                              ssn: str) -> destination_models.SecurityRate:
        """
        Inserts new row into company access table
        Args:
            backend_session: backend database session
            company: company
            ssn: authorized ssn
        """
        company_access = destination_models.CompanyAccess()
        company_access.company_id = company.id
        company_access.ssn = ssn
        backend_session.add(company_access)
        return company_access
