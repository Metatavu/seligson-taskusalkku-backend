import pytest
import os
import logging

from testcontainers.mysql import MySqlContainer
from ..utils.database import mysql_import_sql

logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
container_import_folder = "/tmp/import"  # NOSONAR


@pytest.fixture(scope="session")
def salkku_mysql(request):
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

    mysql_import_sql(mysql, 'salkku-db.sql')

    def teardown():
        """Stops the containers after session
        """
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
