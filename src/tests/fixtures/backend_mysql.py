import pytest
import os
import logging

from alembic.config import Config
from alembic import command
from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)
alembicini = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'alembic.ini')

@pytest.fixture(scope="session")
def backend_mysql(request):
    """MySQL Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        MySqlContainer: Reference to MySQL container
    """

    mysql = MySqlContainer('mysql:5.6')
    mysql.with_command("--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci")
    mysql.start()
    os.environ["DATABASE_URL"] = mysql.get_connection_url()
    alembic_cfg = Config(alembicini)
    command.upgrade(alembic_cfg, 'head')

    def teardown():
        """Stops the containers after session
        """
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
