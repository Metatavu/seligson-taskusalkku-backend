import logging
import os
import sys
from datetime import datetime

import click
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import models

logger = logging.getLogger(__name__)


class KiidMigrateHandler:
    """
    Migration handler from KIID database
    """

    def __init__(self, debug: bool):
        """
        Constructor
        Args:
            debug: whether to run the command in debug mode
        """
        self.kiid_engine, self.backend_engine = self.get_sessions()
        self.debug = debug
        self.start_time = None

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

    def handle(self):
        """
        Handles the migration
        """
        self.start_time = datetime.now()
        self.print_message(f"Start time: {self.start_time}")

        synchronized_count = 0
        with Session(self.kiid_engine) as kiid_session, Session(
                self.backend_engine) as backend_session:

            fund_rows = self.list_fund_rows(kiid_session=kiid_session)
            for fund_row in fund_rows:
                fund_id = fund_row.ID

                fund: models.Fund = backend_session.query(models.Fund) \
                    .filter(models.Fund.original_id == fund_id) \
                    .one_or_none()

                if not fund:
                    fund = models.Fund()
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
                backend_session.flush()
                synchronized_count = synchronized_count + 1

            if not self.debug:
                backend_session.commit()
                self.print_message(f"\nSynchronized {synchronized_count} funds.")
            else:
                self.print_message(f"\nSynchronized {synchronized_count} funds. Nothing changed (in debug mode)")

            end_time = datetime.now()
            total_time = end_time - self.start_time

            self.print_message(f"End time: {end_time}, total time: {total_time}")

    @staticmethod
    def get_sessions() -> (MockConnection, MockConnection):
        """
        Initializes database sessions
        Returns: database sessions
        """
        kiid_database_url = os.environ.get("KIID_DATABASE_URL", "")
        backend_database_url = os.environ.get("BACKEND_DATABASE_URL", "")
        if not kiid_database_url or not backend_database_url:
            raise Exception("environment variables are not set")
        else:
            kiid_engine = create_engine(kiid_database_url)
            backend_engine = create_engine(backend_database_url)
            return kiid_engine, backend_engine

    def print_message(self, message: str):
        """
        Prints message
        Args:
            message: message
        """
        if self.debug:
            click.echo(f"{message}")
        else:
            logger.warning(message)


@click.command()
@click.option("--debug", default=False, help="Debug, readonly for testing purposes")
def main(debug):
    """Migration method"""
    handler = KiidMigrateHandler(debug=debug)
    handler.handle()


if __name__ == '__main__':
    main()
