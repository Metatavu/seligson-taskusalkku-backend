import pytest
import os
import logging

from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
container_import_folder = "/tmp/import"  # NOSONAR


def mysql_import_sql(mysql: MySqlContainer, sql_import_file: str):
    logger.info(f"Importing SQL file {sql_import_file}...")
    import_command = f'bash -c "mysql -uroot -ptest test < {container_import_folder}/{sql_import_file}"'
    import_result = mysql.exec(import_command)
    assert import_result.exit_code == 0


@pytest.fixture(scope="session")
def mysql(request):
    """MySQL Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        MySqlContainer: Reference to MySQL container
    """

    mysql = MySqlContainer('mariadb:10.3.29')
    mysql.with_volume_mapping(data_dir, container_import_folder)
    mysql.with_command("--server-id=1 --log-bin=/var/log/mysql/mysql-bin.log --binlog_format=ROW --binlog_do_db=test")
    mysql.start()
    os.environ["SQLALCHEMY_DATABASE_URL"] = mysql.get_connection_url()

    mysql_import_sql(mysql, 'db.sql')
    mysql_import_sql(mysql, 'fund-securities.sql')
    mysql_import_sql(mysql, 'raterah.sql')

    def teardown():
        """Stops the containers after session
        """
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
