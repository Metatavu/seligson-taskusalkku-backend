import pytest
import os
import logging

from alembic.config import Config
from alembic import command
from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
container_import_folder = "/tmp/import"  # NOSONAR
alembicini = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'alembic.ini')

@pytest.fixture(scope="session")
def backend_mysql(request):
    """MySQL Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        MySqlContainer: Reference to MySQL container
    """

    mysql = MySqlContainer('mariadb:10.3.29')
    mysql.with_volume_mapping(data_dir, container_import_folder)
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
