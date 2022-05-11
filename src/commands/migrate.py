import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi_mail import MessageSchema
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session

import click

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands.migration_tasks import AbstractMigrationTask, MigrateFundsTask, MigrateSecuritiesTask, \
    MigrateSecurityRatesTask, MigrateLastRatesTask, MigrateCompaniesTask, MigratePortfoliosTask, \
    MigrateCompanyAccessTask, MigratePortfolioLogsTask, MigratePortfolioTransactionsTask

from commands.migration_exceptions import MigrationException, MissingEntityException
from database.models import SynchronizationFailure
from mail.mailer import Mailer

logger = logging.getLogger(__name__)

SYNCHRONIZATION_FAILURE_ACTION_FORCE = 1
SYNCHRONIZATION_FAILURE_ACTION_NOTIFIED = 2


class MigrateHandler:

    tasks = [MigrateFundsTask(), MigrateSecuritiesTask(), MigrateSecurityRatesTask(), MigrateLastRatesTask(),
             MigrateCompaniesTask(), MigrateCompanyAccessTask(), MigratePortfoliosTask(),
             MigratePortfolioTransactionsTask(), MigratePortfolioLogsTask()]

    """
    Migration handler database
    """

    def __init__(self, debug: bool, force_recheck: bool, timeout: int, security: str, verify_only: bool):
        """
        Constructor
        Args:
            debug: whether to run the command in debug mode
            force_recheck: Whether task should be forced to recheck all entities
        """
        self.backend_engine = self.get_backend_engine()
        self.debug = debug
        self.force_recheck = force_recheck
        self.timeout = timeout
        self.force_failed_tasks = []
        self.forced_failed_tasks = []
        self.security = security
        self.verify_only = verify_only

    async def handle(self,
                     task_name: Optional[str],
                     skip_tasks: Optional[List[str]] = None
                     ):
        """
        Runs migrations
        Args:
            task_name: name of the task to run. Runs everything is not specified
            skip_tasks: list of tasks to skip
        """
        timeout = datetime.now() + timedelta(minutes=self.timeout)
        result = True
        task_names = []

        if task_name:
            task_names = [task_name]
        else:
            task_names = map(lambda x: x.get_name(), self.tasks)

        if skip_tasks is not None:
            task_names = list(filter(lambda x: x not in skip_tasks, task_names))

        with Session(self.backend_engine) as backend_session:
            self.force_failed_tasks = self.list_force_failed_tasks(backend_session)

        self.print_message(f"\nRunning tasks: {task_names}")

        self.force_failed_tasks = list(filter(lambda x: x in task_names, self.force_failed_tasks))

        if len(self.force_failed_tasks) > 0:
            self.print_message(f"\nForcing failed tasks: {self.force_failed_tasks}")

        for task in self.tasks:
            task.options = {
                "security": self.security
            }

            if not self.verify_only and result and (timeout > datetime.now()) and (task.get_name() in task_names):
                result = await self.run_task(task, timeout, False)

            if result and (timeout > datetime.now()) and (task.get_name() in task_names):
                valid = await self.run_verify(task=task)
                if not valid:
                    if not self.verify_only:
                        self.print_message(f"Warning: Verification failed on {task.get_name()}, forcing the task...")
                        await self.run_task(task, timeout, True)
                        valid = await self.run_verify(task=task)

                        if not valid:
                            self.print_message(f"Warning: Verification failed on {task.get_name()}, "
                                               f"despite of forcing the tasl. Notifying administrators...")
                            await self.notify_verification_failure(task)
                    else:
                        self.print_message(f"Warning: Verification failed on {task.get_name()}.")
                else:
                    self.print_message(f"Info: {task.get_name()} verification passed.")

        if len(self.forced_failed_tasks) > 0:
            with Session(self.backend_engine) as backend_session:
                self.mark_forced_tasks_as_done(backend_session=backend_session)
                backend_session.commit()

    async def run_task(self, task: AbstractMigrationTask, timeout: datetime, force: bool) -> bool:
        """
        Runs single migration task
        Args:
            task: task
            timeout: timeout
            force: whether to force task
        """
        result = True
        start_time = datetime.now()
        name = task.get_name()
        self.print_message(f"Start time: {start_time}")

        with Session(self.backend_engine) as backend_session:
            task.prepare(backend_session=backend_session)
            force_failed_task = name in self.force_failed_tasks

            if force or self.force_recheck or force_failed_task:
                self.print_message(f"\nForced recheck, migrating {name}...")

                try:
                    count = task.migrate(backend_session=backend_session,
                                         timeout=timeout,
                                         force_recheck=True)
                    self.print_message(f"\n{name} migration complete. {count} updated entries")

                    if force_failed_task:
                        self.forced_failed_tasks.append(name)

                except MissingEntityException as e:
                    await self.handle_synchronization_failure(
                        backend_session=backend_session,
                        original_id=e.original_id,
                        message=e.message,
                        target_task=e.target_task,
                        origin_task=name
                    )

                    result = False
            else:
                up_to_date = task.up_to_date(backend_session)
                if up_to_date:
                    self.print_message(f"\n{name} is already up-to-date.")
                else:
                    self.print_message(f"\n{name} is not up-to-date. Migrating...")

                    try:
                        count = task.migrate(backend_session=backend_session,
                                             timeout=timeout,
                                             force_recheck=self.force_recheck)
                        self.print_message(f"\n{name} migration complete. {count} updated entries")
                    except MissingEntityException as e:
                        await self.handle_synchronization_failure(
                            backend_session=backend_session,
                            original_id=e.original_id,
                            message=e.message,
                            target_task=e.target_task,
                            origin_task=name
                        )

                        result = False

            if not self.debug:
                backend_session.commit()
                self.print_message(f"\nSaved changes.")
            else:
                self.print_message(f"\nRunning in debug mode, not saving the changes")

            end_time = datetime.now()
            total_time = end_time - start_time

            self.print_message(f"Success: {result}, End time: {end_time}, total time: {total_time}")
            return result

    async def run_verify(self, task: AbstractMigrationTask):
        """
        Runs the verification task.
        Args:
            task: the task to run

        Returns:
            True if the verification was successful, False otherwise
        """
        name = task.get_name()

        with Session(self.backend_engine) as backend_session:
            if task.verify(backend_session=backend_session):
                return True
            else:
                return False

    async def handle_synchronization_failure(self,
                                             backend_session: Session,
                                             original_id: str,
                                             message: str,
                                             origin_task: str,
                                             target_task: str
                                             ):
        """
        Handles synchronization failure.

        Args:
            backend_session: The backend session.
            original_id: The original id of the entity.
            message: The message to be added to the database.
            origin_task: Task where failure was detected.
            target_task: Task where failure should be handled.
        """
        if target_task not in self.force_failed_tasks:
            self.print_message(f"Error: synchronization failure on {origin_task}: {message}. "
                               f"Requesting force sync for {target_task}")

            await self.add_synchronization_failure(
                backend_session=backend_session,
                target_task=target_task,
                origin_task=origin_task,
                message=message,
                original_id=original_id
            )
        else:
            self.print_message(f"Error: synchronization failure on {origin_task}: {message}. "
                               f"Force synchronization of {target_task} was already done so notifying administrators")

            await self.notify_synchronization_failure(
                backend_session=backend_session,
                target_task=target_task
            )

    async def add_synchronization_failure(self,
                                          backend_session: Session,
                                          original_id: str,
                                          message: str,
                                          target_task: str,
                                          origin_task: str
                                          ):
        """
        Adds a synchronization failure to the database and marks target task to be forced next time.

        Args:
            backend_session: The backend session.
            original_id: The original id of the entity.
            message: The message to be added to the database.
            origin_task: Task where failure was detected.
            target_task: Task where failure should be handled.

        Returns: created synchronization failure
        """

        existing_synchronization_failure = backend_session.query(SynchronizationFailure.target_task) \
            .filter(SynchronizationFailure.handled.is_(False)) \
            .filter(SynchronizationFailure.target_task == target_task) \
            .one_or_none()

        if existing_synchronization_failure is not None:
            self.print_message(f"Warning: Failure for {target_task} already requested.")
            return existing_synchronization_failure
        else:
            synchronization_failure = SynchronizationFailure()
            synchronization_failure.original_id = original_id
            synchronization_failure.message = message
            synchronization_failure.target_task = target_task
            synchronization_failure.origin_task = origin_task
            synchronization_failure.handled = False
            synchronization_failure.action = SYNCHRONIZATION_FAILURE_ACTION_FORCE
            synchronization_failure.created = datetime.now()
            synchronization_failure.updated = datetime.now()
            backend_session.add(synchronization_failure)
            return synchronization_failure

    async def notify_synchronization_failure(self,
                                             backend_session: Session,
                                             target_task: str
                                             ):
        """
        Notifies administrators about synchronization failure.

        Args:
            backend_session: The backend session.
            target_task: Task where failure should have been fixed
        Returns:

        """
        synchronization_failure = backend_session.query(SynchronizationFailure) \
            .filter(SynchronizationFailure.handled.is_(False)) \
            .filter(SynchronizationFailure.target_task == target_task) \
            .filter(SynchronizationFailure.action == SYNCHRONIZATION_FAILURE_ACTION_FORCE) \
            .one()

        origin_task = synchronization_failure.origin_task
        message = synchronization_failure.message
        email_body = f"Portfolios synchronization failed.\n\n" \
                     f"Error details:\n\n" \
                     f"Origin task: {origin_task}\n" \
                     f"Target task: {target_task}\n" \
                     f"Message: {message}\n" \
                     f"Status: {target_task} already forced\n\n" \
                     f"This is an automated message, please do not reply to this email"

        message = MessageSchema(
            subject=f"Synchronization failure on Taskusalkku",
            recipients=os.environ["MAIL_SYNCHRONIZATION_FAILURE_RECIPIENTS"].split(","),
            body=email_body
        )

        try:
            await Mailer.send_mail(message)
        except Exception as e:
            self.print_message(f"Error sending email {e}")

        synchronization_failure.handled = True
        synchronization_failure.updated = datetime.now()
        synchronization_failure.action = SYNCHRONIZATION_FAILURE_ACTION_NOTIFIED
        backend_session.add(synchronization_failure)

    async def notify_verification_failure(self, task):
        """
        Notifies verification failure

        Args:
            task: task
        """
        task_name = task.get_name()
        email_body = f"Data verification failed on {task_name}.\n\n" \
                     f"This is an automated message, please do not reply to this email"

        message = MessageSchema(
            subject=f"Data verification failure on Taskusalkku",
            recipients=os.environ["MAIL_SYNCHRONIZATION_FAILURE_RECIPIENTS"].split(","),
            body=email_body
        )

        try:
            await Mailer.send_mail(message)
        except Exception as e:
            self.print_message(f"Error sending email {e}")

    @staticmethod
    def list_force_failed_tasks(backend_session: Session) -> List[str]:
        """
        Lists all tasks that have are marked for force synchronization.

        Args:
            backend_session: The backend session.
        """
        result = backend_session.query(SynchronizationFailure.target_task) \
            .filter(SynchronizationFailure.handled.is_(False)) \
            .filter(SynchronizationFailure.action == SYNCHRONIZATION_FAILURE_ACTION_FORCE)\
            .all()
        return [r[0] for r in result]

    def mark_forced_tasks_as_done(self, backend_session: Session):
        """
        Marks all tasks that are marked for force synchronization as done.

        Args:
            backend_session: The backend session.
        """
        for task in self.forced_failed_tasks:
            self.print_message(f"Marking forced task {task} as done")
            synchronization_failure = backend_session.query(SynchronizationFailure) \
                .filter(SynchronizationFailure.handled.is_(False)) \
                .filter(SynchronizationFailure.target_task == task) \
                .filter(SynchronizationFailure.action == SYNCHRONIZATION_FAILURE_ACTION_FORCE) \
                .one_or_none()
            if synchronization_failure is not None:
                synchronization_failure.handled = True
                backend_session.add(synchronization_failure)

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
@click.option("--skip-tasks", default="", help="Run without specified tasks")
@click.option("--force-recheck", default=False, help="Forces task to recheck all entities")
@click.option("--timeout", default="15", help="Timeout in minutes")
@click.option("--security", default=None, help="Specify security for the task")
@click.option("--verify-only", default=False, help="Runs only verifications")
def main(debug, task, skip_tasks, force_recheck, timeout, security, verify_only):
    """Migration method"""
    handler = MigrateHandler(
        debug=debug,
        force_recheck=force_recheck,
        timeout=int(timeout),
        security=security,
        verify_only=verify_only
    )

    asyncio.run(handler.handle(
        task_name=task,
        skip_tasks=skip_tasks
    ))


if __name__ == '__main__':
    main()
