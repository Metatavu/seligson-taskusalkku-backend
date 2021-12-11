import contextlib
import time
from datetime import datetime, timedelta
import logging
from typing import Any

from testcontainers.mysql import MySqlContainer
from testcontainers.mssql import SqlServerContainer
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
container_import_folder = "/tmp/import"  # NOSONAR


def mysql_exec_sql(mysql: MySqlContainer, sql_file: str):
    """Import SQL file into test database

    Args:
        mysql (MySqlContainer): database container
        sql_file (str): file
    """
    logger.info(f"Importing SQL file {sql_file}...")
    import_command = f'bash -c "mysql -uroot -ptest test < {container_import_folder}/{sql_file}"'
    import_result = mysql.exec(import_command)
    assert import_result.exit_code == 0, f"Error while importing {sql_file}: {import_result.output.decode('utf-8')}"


def mssql_exec_sql(mssql: SqlServerContainer, sql_file: str):
    """Import SQL file into test database
    Args:
        mssql (SqlServerContainer): database container
        sql_file (str): file
    """
    logger.info(f"Importing SQL file {sql_file}...")
    import_file = f"{container_import_folder}/{sql_file}"
    import_command = f'bash -c "/opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U sa -P Test1234. -i {import_file}"'
    import_result = mssql.exec(import_command)
    assert import_result.exit_code == 0, import_result.output.decode("utf-8")

@contextlib.contextmanager
def sql_backend_funds(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-funds.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-funds-teardown.sql")


@contextlib.contextmanager
def sql_backend_security_rates(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-security-rates.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-security-rates-teardown.sql")


@contextlib.contextmanager
def sql_salkku_fund_securities(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="salkku-fund-securities.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="salkku-fund-securities-teardown.sql")


@contextlib.contextmanager
def sql_funds_rate(mssql: SqlServerContainer):
    try:
        yield mssql_exec_sql(mssql=mssql, sql_file="funds-rate.sql")
    finally:
        mssql_exec_sql(mssql=mssql, sql_file="funds-rate-teardown.sql")


@contextlib.contextmanager
def sql_backend_company(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-company.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-company-teardown.sql")


@contextlib.contextmanager
def sql_backend_security(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-security.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-security-teardown.sql")


@contextlib.contextmanager
def sql_backend_last_rate(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-last-rate.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-last-rate-teardown.sql")


@contextlib.contextmanager
def sql_backend_portfolio(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio-teardown.sql")


@contextlib.contextmanager
def sql_backend_portfolio_transaction(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio-transaction.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio-transaction-teardown.sql")


@contextlib.contextmanager
def sql_backend_portfolio_log(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio-log.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-portfolio-log-teardown.sql")


def wait_for_row_count(engine, entity: Any, count: int):
    """Waits for table row count to match given count

    Args:
        engine (Engine): SQL Alchemy engine
        entity (Any): SQL Alchemy entity
        count (int): count
    """    
    current = None
    timeout = datetime.now() + timedelta(seconds=120)
    
    while current != count:
        time.sleep(0.5)
        with Session(engine) as session:
            current = session.query(entity).count()
        logger.info("Waiting for count to be %s...", count)

        assert datetime.now() < timeout, f"Timed out waiting for count to be {count}, current count is {current}"
