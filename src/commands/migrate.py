import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session

import click

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands.migration_exception import MigrationException
from commands.migration_tasks import AbstractMigrationTask, MigrateFundsTask, MigrateSecuritiesTask, \
    MigrateSecurityRatesTask, MigrateLastRatesTask, MigrateCompaniesTask, MigratePortfoliosTask, \
    MigratePortfolioLogsTask, MigratePortfolioTransactionsTask

logger = logging.getLogger(__name__)


class MigrateHandler:

    tasks = [MigrateFundsTask(), MigrateSecuritiesTask(), MigrateSecurityRatesTask(), MigrateLastRatesTask(),
             MigrateCompaniesTask(), MigratePortfoliosTask(), MigratePortfolioTransactionsTask(),
             MigratePortfolioLogsTask()]

    """
    Migration handler database
    """

    def __init__(self, debug: bool, force_recheck: bool):
        """
        Constructor
        Args:
            debug: whether to run the command in debug mode
            force_recheck: Whether task should be forced to recheck all entities
        """
        self.backend_engine = self.get_backend_engine()
        self.debug = debug
        self.force_recheck = force_recheck

    def handle(self, task_name: Optional[str]):
        """
        Runs migrations
        Args:
            task_name: name of the task to run. Runs everything is not specified

        """
        timeout = datetime.now() + timedelta(minutes=15)

        for task in self.tasks:
            if timeout > datetime.now() and (not task_name or task_name == task.get_name()):
                self.run_task(task, timeout)

    def run_task(self, task: AbstractMigrationTask, timeout: datetime):
        """
        Runs single migration task
        Args:
            task: task
            timeout: timeout
        """
        start_time = datetime.now()
        name = task.get_name()
        self.print_message(f"Start time: {start_time}")

        with Session(self.backend_engine) as backend_session:
            task.prepare(backend_session=backend_session)

            if self.force_recheck:
                self.print_message(f"\nForced recheck, migrating {name}...")
                count = task.migrate(backend_session=backend_session,
                                     timeout=timeout,
                                     force_recheck=self.force_recheck)
                self.print_message(f"\n{name} migration complete. {count} updated entries")
            else:
                up_to_date = task.up_to_date(backend_session)
                if up_to_date:
                    self.print_message(f"\n{name} is already up-to-date.")
                else:
                    self.print_message(f"\n{name} is not up-to-date. Migrating...")
                    count = task.migrate(backend_session=backend_session,
                                         timeout=timeout,
                                         force_recheck=self.force_recheck)
                    self.print_message(f"\n{name} migration complete. {count} updated entries")

            if not self.debug:
                backend_session.commit()
                self.print_message(f"\nSaved changes.")
            else:
                self.print_message(f"\nRunning in debug mode, not saving the changes")

            end_time = datetime.now()
            total_time = end_time - start_time

            self.print_message(f"End time: {end_time}, total time: {total_time}")

    @staticmethod
    def get_backend_engine() -> MockConnection:
        """
        Initializes backend database engine
        """
        backend_database_url = os.environ.get("BACKEND_DATABASE_URL", "")
        if not backend_database_url:
            raise MigrationException("BACKEND_DATABASE_URL environment variable is not set")
        else:
            return create_engine(backend_database_url)

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
@click.option("--task", default="", help="Only run specified task")
@click.option("--force-recheck", default=False, help="Forces task to recheck all entities")
def main(debug, task, force_recheck):
    """Migration method"""
    handler = MigrateHandler(debug=debug, force_recheck=force_recheck)
    handler.handle(task)


if __name__ == '__main__':
    main()
