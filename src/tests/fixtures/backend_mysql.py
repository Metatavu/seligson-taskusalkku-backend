import pytest
import os
import logging

from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def backend_mysql(request):
    """MySQL Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        MySqlContainer: Reference to MySQL container
    """

    mysql = MySqlContainer('mysql:5.6')
    mysql.start()
    os.environ["DATABASE_URL"] = mysql.get_connection_url()

    def teardown():
        """Stops the containers after session
        """
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
