import os
import logging
from decimal import Decimal

from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, and_, func
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
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

    @staticmethod
    def get_excluded_por_ids_query():
        """
        Returns exclude query for excluded porids
        Returns: exclude query for excluded porids
        """
        return "SELECT DISTINCT P.PORID " \
               "FROM TABLE_PORTFOL P " \
               "INNER JOIN TABLE_PORCLASSDEF D ON P.COM_CODE = D.COM_CODE " \
               "AND P.PORID = D.PORID AND D.PORCLASS IN (3, 4, 5)"


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
                    backend_session=backend_session, original_id=original_security_id)

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
        return "security-rates"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = backend_session.execute(statement="SELECT COUNT(ID) FROM security_rate").fetchone()[0]
            funds_count = funds_session.execute(statement="SELECT COUNT(*) FROM TABLE_RATE").fetchone()[0]
            return backend_count >= funds_count

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        batch = 1000

        with Session(self.get_funds_database_engine()) as funds_session:
            last_funds_dates = self.get_last_funds_dates(funds_session=funds_session)
            last_backend_dates = self.get_last_backend_dates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if self.should_timeout(timeout=timeout):
                    break

                offset = 0

                last_fund_date = last_funds_dates.get(security.original_id, None)
                if not last_fund_date:
                    continue

                last_backend_date = last_backend_dates.get(security.id, date(1970, 1, 1))

                if last_fund_date <= last_backend_date:
                    continue

                while not self.should_timeout(timeout=timeout):
                    self.print_message(f"Migrating security {security.original_id} rates from offset {offset}")

                    rate_rows = self.list_security_rates(
                        funds_session=funds_session,
                        security=security,
                        rdate=last_backend_date,
                        offset=offset,
                        limit=batch
                    )

                    if rate_rows.rowcount == 0:
                        break

                    for rate_row in rate_rows:
                        rate_date = rate_row[0]
                        rate_close = rate_row[1]

                        has_rate = offset == 0 and self.has_security_rate(
                            backend_session=backend_session,
                            security=security,
                            rate_date=rate_date
                        )

                        if not has_rate:
                            self.insert_security_rate(
                                backend_session=backend_session,
                                security=security,
                                rate_date=rate_date,
                                rate_close=rate_close
                            )

                            synchronized_count = synchronized_count + 1

                    if rate_rows.rowcount < batch:
                        break

                    offset += batch

            if self.should_timeout(timeout=timeout):
                self.print_message("Timed out.")

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
    def list_security_rates(funds_session: Session, security: destination_models.Security, rdate: datetime,
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
    def has_security_rate(backend_session: Session, security: destination_models.Security, rate_date: date) -> bool:
        """
        Returns whether rate exists for given security and date
        Args:
            backend_session: backend database session
            security: security
            rate_date: date

        Returns: whether rate exists for given security and date
        """
        return backend_session.query(destination_models.SecurityRate.id) \
            .filter(and_(destination_models.SecurityRate.security_id == security.id,
                         destination_models.SecurityRate.rate_date == rate_date)) \
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


class MigrateLastRatesTask(AbstractFundsTask):
    """
    Migration task for last rates
    """

    def get_name(self):
        return "last-rate"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = backend_session.execute(statement="SELECT COUNT(ID) FROM last_rate").fetchone()[0]
            funds_count = funds_session.execute(statement="SELECT COUNT(*) FROM TABLE_RATELAST").fetchone()[0]
            return backend_count >= funds_count

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0

        with Session(self.get_funds_database_engine()) as funds_session:

            rate_last_rows = funds_session.execute("SELECT SECID, RDATE, RCLOSE FROM TABLE_RATELAST")
            for rate_last_row in rate_last_rows:
                security = self.get_security_by_original_id(backend_session=backend_session,
                                                            original_id=rate_last_row.SECID)
                if not security:
                    raise MigrationException(f"Could not find security {rate_last_row.SECID}")

                existing_last_rate: destination_models.LastRate = backend_session.query(
                    destination_models.LastRate).filter(
                    destination_models.LastRate.security_id == security.id).one_or_none()

                self.upsert_last_rate(backend_session=backend_session,
                                      last_rate=existing_last_rate,
                                      security_id=security.id,
                                      rate_close=rate_last_row.RCLOSE
                                      )
                synchronized_count = synchronized_count + 1

            return synchronized_count

    @staticmethod
    def upsert_last_rate(backend_session, last_rate, security_id, rate_close) -> destination_models.LastRate:

        new_last_rate = last_rate if last_rate else destination_models.LastRate()
        new_last_rate.security_id = security_id
        new_last_rate.rate_close = rate_close
        backend_session.add(new_last_rate)
        return new_last_rate


class MigrateCompaniesTask(AbstractFundsTask):
    """
    Migration task for companies
    """

    def get_name(self):
        return "companies"

    def up_to_date(self, backend_session: Session) -> bool:
        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = self.count_backend_companies(backend_session=backend_session)
            funds_count = self.count_fund_companies(funds_session=funds_session)
            return funds_count == backend_count

    @staticmethod
    def count_backend_companies(backend_session: Session):
        """
        Counts backend database companies
        Args:
            backend_session: backend database session

        Returns: backend database company count

        """
        return backend_session.query(func.count(destination_models.Company.id)).scalar()

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        batch = 1000
        offset = 0

        with Session(self.get_funds_database_engine()) as funds_session:
            backend_count = self.count_backend_companies(backend_session=backend_session)
            funds_count = self.count_fund_companies(funds_session=funds_session)

            if backend_count > funds_count:
                self.print_message(f"Backend company count exceeds funds company count. Purging extra companies")
                valid_com_codes = self.list_company_com_codes(funds_session=funds_session)
                backend_session.query(destination_models.Company)\
                    .filter(destination_models.Company.original_id.not_in(valid_com_codes))\
                    .delete(synchronize_session=False)
            else:
                offset = backend_count

            while not self.should_timeout(timeout=timeout):
                self.print_message(f"Migrating companies from offset {offset}")

                company_rows = self.list_companies(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if company_rows.rowcount == 0:
                    break

                for company_row in company_rows:
                    com_code = company_row[0]
                    so_sec_nr = company_row[1]

                    existing_company = self.get_company_by_original_id(backend_session=backend_session,
                                                                       original_id=com_code)

                    if not existing_company:
                        self.insert_company(
                            backend_session=backend_session,
                            original_id=com_code,
                            ssn=so_sec_nr
                        )

                        synchronized_count = synchronized_count + 1

                offset += batch

            if self.should_timeout(timeout=timeout):
                self.print_message("Timed out.")

            return synchronized_count

    def count_fund_companies(self, funds_session: Session) -> int:
        """
        Counts companies from funds database
        Args:
            funds_session: Funds database session

        Returns: company count from funds database
        """
        excluded = self.get_excluded_com_codes_query()
        return funds_session\
            .execute(f"SELECT count(COM_CODE) FROM TABLE_COMPANY WHERE COM_TYPE = '3' "
                     f"AND COM_CODE NOT IN ({excluded})") \
            .fetchone()[0]

    def list_company_com_codes(self, funds_session: Session):
        """
        Lists company com codes from funds database
        Args:
            funds_session: Funds database session

        Returns: company com codes from funds database
        """
        excluded = self.get_excluded_com_codes_query()
        rows = funds_session.execute(f"SELECT COM_CODE FROM TABLE_COMPANY "
                                     f"WHERE COM_TYPE = '3' AND COM_CODE NOT IN ({excluded})")
        return list(map(lambda i: i.COM_CODE, rows))

    def list_companies(self, funds_session: Session, limit: int, offset: int):
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
            f"SELECT COM_CODE, SO_SEC_NR FROM TABLE_COMPANY WHERE COM_TYPE = '3' AND COM_CODE NOT IN ({excluded}) "
            "ORDER BY CREA_DATE OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY",
            {
                "limit": limit,
                "offset": offset
            })

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
    def insert_company(backend_session: Session, original_id: str, ssn: str) -> destination_models.Company:
        """
        Inserts new company
        Args:
            backend_session: backend database session
            original_id: original id
            ssn: ssn

        Returns: created company
        """
        new_company = destination_models.Company()
        new_company.original_id = original_id
        new_company.ssn = ssn
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
            funds_count = funds_session.execute(statement="SELECT COUNT(COM_CODE) FROM TABLE_PORTFOL").fetchone()[0]
            return backend_count >= funds_count

    @staticmethod
    def count_backend_portfolios(backend_session: Session):
        """
        Counts backend database portfolios
        Args:
            backend_session: backend database session

        Returns: backend database portfolio count

        """
        return backend_session.query(func.count(destination_models.Portfolio.id)).scalar()

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        batch = 1000
        offset = self.count_backend_portfolios(backend_session=backend_session)

        with Session(self.get_funds_database_engine()) as funds_session:

            while not self.should_timeout(timeout=timeout):
                self.print_message(f"Migrating portfolios from offset {offset}")

                portfolio_rows = self.list_portfolios(
                    funds_session=funds_session,
                    offset=offset,
                    limit=batch
                )

                if portfolio_rows.rowcount == 0:
                    break

                for portfolio_row in portfolio_rows:
                    por_id = portfolio_row[0]
                    name = portfolio_row[1]
                    com_code = portfolio_row[2]

                    existing_portfolio = self.get_portfolio_id_by_original_id(backend_session=backend_session,
                                                                              original_id=por_id)
                    if not existing_portfolio:
                        company = self.get_company_by_original_id(backend_session=backend_session, original_id=com_code)
                        if not company:
                            raise MigrationException(f"Could not find company {com_code}")

                        self.insert_portfolio(
                            backend_session=backend_session,
                            original_id=por_id,
                            company_id=company.id,
                            name=name
                        )

                        synchronized_count = synchronized_count + 1

                if portfolio_rows.rowcount < batch:
                    break

                offset += batch

            if self.should_timeout(timeout=timeout):
                self.print_message("Timed out.")

            return synchronized_count

    def list_portfolios(self, funds_session: Session, limit: int, offset: int):
        """
        Lists portfolios from funds database
        Args:
            funds_session: Funds database session
            limit: max results
            offset: offset

        Returns: portfolios from funds database
        """
        exclude_query = self.get_excluded_por_ids_query()
        return funds_session.execute('SELECT PORID, NAME1, COM_CODE FROM TABLE_PORTFOL '
                                     f'WHERE PORID NOT IN ({exclude_query})'
                                     'ORDER BY COM_CODE OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY',
                                     {
                                         "limit": limit,
                                         "offset": offset
                                     })

    @staticmethod
    def insert_portfolio(backend_session: Session, original_id: str, company_id: UUID, name: str) -> \
            destination_models.Portfolio:
        """
        Creates new portfolio
        Args:
            backend_session: backend database session
            original_id: original id
            company_id: company id
            name: name

        Returns: created portfolio
        """
        new_portfolio = destination_models.Portfolio()
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

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        batch = 1000
        unix_time = datetime(1970, 1, 1, 0, 0)

        with Session(self.get_funds_database_engine()) as funds_session:

            funds_updates = self.get_funds_updates(funds_session=funds_session)
            backend_updates = self.get_backend_updates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if self.should_timeout(timeout=timeout):
                    break

                offset = 0

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
                                raise MigrationException(f"Could not find security {c_security_original_id}")

                            c_security_id = c_security.id
                        else:
                            c_security_id = None

                        portfolio_original_id = portfolio_log_row.PORID
                        if portfolio_original_id:
                            portfolio_id = portfolio_id_map.get(portfolio_original_id, None)
                            if not portfolio_id:
                                raise MigrationException(f"Could not find portfolio {portfolio_original_id}")

                        else:
                            # without the portfolio key we cant do anything, we try to grab the right portfolio from
                            # portfolio table considering the company code. If there are more than one portfolio then
                            # we should alert and ask how to resolve the situation manually.
                            company = self.get_company_by_original_id(backend_session=backend_session,
                                                                      original_id=portfolio_log_row.COM_CODE)
                            if not company:
                                raise MigrationException(f"Could not find company {portfolio_log_row.COM_CODE}")

                            portfolios = self.list_portfolios_by_company(backend_session=backend_session,
                                                                         company_id=company.id)
                            if len(portfolios) != 1:
                                raise MigrationException(f"Could not resolve portfolio for company "
                                                         f"{portfolio_log_row.COM_CODE}")

                            else:
                                portfolio = portfolios[0]
                                portfolio_id = portfolio.id

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
                self.print_message("Timed out.")

            return synchronized_count

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
        porid_exclude_query = self.get_excluded_por_ids_query()

        return funds_session.execute("SELECT SECID, CSECID, PORID, COM_CODE, TRANS_NR, TRANS_CODE, TRANS_DATE, "
                                     "CTOT_VALUE, AMOUNT, CPRICE, PMT_DATE, CVALUE, PROVISION, STATUS, "
                                     "UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) as UPDATED "
                                     "FROM TABLE_PORTLOG "
                                     "WHERE UPD_DATE + CAST(REPLACE(UPD_TIME, '.', ':') as DATETIME) >= :updated AND "
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
    def upsert_portfolio_log(session, portfolio_log, transaction_number, transaction_code, transaction_date,
                             c_total_value,
                             portfolio_id, security_id, c_security_id, amount, c_price, payment_date, c_value,
                             provision, status, updated: datetime):
        new_portfolio_log = portfolio_log if portfolio_log else destination_models.PortfolioLog()
        new_portfolio_log.transaction_number = transaction_number
        new_portfolio_log.transaction_code = transaction_code
        new_portfolio_log.transaction_date = transaction_date
        new_portfolio_log.c_total_value = c_total_value
        new_portfolio_log.portfolio_id = portfolio_id
        new_portfolio_log.security_id = security_id
        new_portfolio_log.c_security_id = c_security_id
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

    def migrate(self, backend_session: Session, timeout: datetime) -> int:
        synchronized_count = 0
        batch = 1000

        with Session(self.get_funds_database_engine()) as funds_session:

            funds_updates = self.get_funds_updates(funds_session=funds_session)
            backend_updates = self.get_backend_updates(backend_session=backend_session)

            securities = self.list_securities(backend_session=backend_session)
            for security in securities:
                if self.should_timeout(timeout=timeout):
                    break

                offset = 0

                funds_updated = funds_updates.get(security.original_id, None)
                if not funds_updated:
                    continue

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

                    existing_transactions = backend_session.query(destination_models.PortfolioTransaction)\
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
                            raise MigrationException(f"Could not find portfolio {portfolio_original_id}")

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
                self.print_message("Timed out.")

            return synchronized_count

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
        excluded = self.get_excluded_por_ids_query()
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
        porid_exclude_query = self.get_excluded_por_ids_query()
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
