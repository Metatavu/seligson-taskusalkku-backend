import pytest
import os
import logging

from ..testcontainers.mssql import SqlServerContainer
from ..utils.database import mssql_exec_sql

logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
container_import_folder = "/tmp/import"  # NOSONAR


@pytest.fixture(scope="session")
def funds_mssql(request):
    """SQL Server Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        SqlServerContainer: Reference to SQL Server container
    """

    mssql = SqlServerContainer(password="Test1234.")
    mssql.with_volume_mapping(data_dir, container_import_folder)
    mssql.start()

    mssql_exec_sql(mssql, 'funds-db.sql')

    def teardown():
        """Stops the containers after session
        """
        mssql.stop()

    request.addfinalizer(teardown)

    return mssql
