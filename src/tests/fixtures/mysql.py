import time
import pytest
import os
import logging

from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
sql_import_files = ['db.sql', 'raterah.sql']
container_import_folder = "/tmp/import"  # NOSONAR


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
    mysql.start()

    for sql_import_file in sql_import_files:
        import_command = f'bash -c "mysql -uroot -ptest test < {container_import_folder}/{sql_import_file}"'
        import_result = mysql.exec(import_command)
        assert import_result.exit_code == 0

    def teardown():
        """Stops the containers after session
        """
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
