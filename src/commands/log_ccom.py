import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session

import click

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Company, PortfolioLog, Security

logger = logging.getLogger(__name__)


class LogCCom:

    """
    Log CCOM migration handler
    """

    async def handle(self):
        """
        Runs migration
        """
        start_time = datetime.now()

        with Session(self.get_backend_engine()) as backend_session:
            backend_companies = list(self.list_backend_companies(backend_session=backend_session))
            backend_company_map = {x.original_id: x for x in backend_companies}

            with Session(self.get_funds_engine()) as funds_session:
                porid_exclude_query = self.get_excluded_portfolio_ids_query()

                backend_securities = self.list_backend_securities(backend_session=backend_session)
                for backend_security in backend_securities:
                    logger.warning(f"Processing security {backend_security.original_id} logs")

                    fund_rows = funds_session.execute(f"SELECT TRANS_NR, CCOM_CODE "
                                                      f"FROM TABLE_PORTLOG "
                                                      f"WHERE SECID = :secid AND PORID NOT IN ({porid_exclude_query}) AND "
                                                      f"CCOM_CODE IS NOT NULL AND TRIM(CCOM_CODE) != ''",
                                                      {
                                                          "secid": backend_security.original_id
                                                      }).fetchall()

                    backend_portfolio_logs = backend_session.query(PortfolioLog)\
                        .filter(PortfolioLog.security_id == backend_security.id) \
                        .all()

                    backend_portfolio_map = {x.transaction_number: x for x in backend_portfolio_logs}

                    rowcount = len(fund_rows)

                    processed = 0
                    for fund_row in fund_rows:
                        company = backend_company_map.get(fund_row.CCOM_CODE, None)
                        if not company:
                            logger.warning(f"Could not find company {fund_row.CCOM_CODE}")

                        portfolio_log = backend_portfolio_map.get(fund_row.TRANS_NR, None)
                        if portfolio_log:
                            portfolio_log.c_company_id = company.id
                            backend_session.add(portfolio_log)

                        processed = processed + 1

                        if processed % 10000 == 0 or processed == rowcount:
                            logger.warning(f"Processed security {backend_security.original_id} "
                                           f"({processed}/{rowcount} rows.)")

                    backend_session.commit()

                end_time = datetime.now()
                total_time = end_time - start_time
                logger.warning(f"All done, end time: {end_time}, total time: {total_time}")

    @staticmethod
    def get_backend_engine() -> MockConnection:
        """
        Initializes backend database engine
        """
        backend_database_url = os.environ.get("BACKEND_DATABASE_URL", "")
        if not backend_database_url:
            raise Exception("BACKEND_DATABASE_URL environment variable is not set")
        else:
            return create_engine(backend_database_url)

    @staticmethod
    def get_funds_engine() -> MockConnection:
        """
        Initializes funds database engine

        Returns:
            engine
        """
        database_url = os.environ.get("FUNDS_DATABASE_URL", "")

        if not database_url:
            raise Exception("FUNDS_DATABASE_URL environment variable is not set")
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
        return backend_session.query(Company).all()

    @staticmethod
    def list_backend_securities(backend_session: Session) -> List[Security]:
        """
        Lists all securities
        Args:
            backend_session: backend database session

        Returns: all securities
        """
        return backend_session.query(Security).all()


@click.command()
def main():
    """Migration method"""
    handler = LogCCom()

    asyncio.run(handler.handle())


if __name__ == '__main__':
    main()
