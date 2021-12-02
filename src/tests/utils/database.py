import contextlib
import time
from datetime import datetime, timedelta
import logging
from typing import Any

from testcontainers.mysql import MySqlContainer
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
    if import_result.exit_code != 0:
        logger.error(import_result.output.decode("utf-8"))

    assert import_result.exit_code == 0

@contextlib.contextmanager
def sql_backend_funds(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-funds.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-funds-teardown.sql")

@contextlib.contextmanager
def sql_backend_fund_rates(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="backend-fund-rates.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="backend-fund-rates-teardown.sql")

@contextlib.contextmanager
def sql_salkku_fund_securities(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="salkku-fund-securities.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="salkku-fund-securities-teardown.sql")

@contextlib.contextmanager
def sql_salkku_raterah(mysql: MySqlContainer):
    try:
        yield mysql_exec_sql(mysql=mysql, sql_file="salkku-raterah.sql")
    finally:
        mysql_exec_sql(mysql=mysql, sql_file="salkku-raterah-teardown.sql")

def wait_for_row_count(engine, entity: Any, count: int):
    """Waits for table row count to match given count

    Args:
        engine (Engine): SQL Alchemy engine
        entity (Any): SQL Alchemy entity
        count (int): count
    """    
    current = None
    timeout = datetime.now() + timedelta(seconds=60)
    
    while current != count:
        time.sleep(0.5)
        with Session(engine) as session:
          current = session.query(entity).count()
        logger.info("Waiting for count to be %s...", count)
        if datetime.now() >= timeout:
            import pdb
            pdb.set_trace()

        assert datetime.now() < timeout, f"Timed out waiting for count to be {count}, current count is {current}"