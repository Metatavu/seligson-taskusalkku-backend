import pytest

from testcontainers.mysql import MySqlContainer


@pytest.fixture(scope="session")
def mysql(request):
    """MySQL Fixture.

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        MySqlContainer: Reference to MySQL container
    """    

    mysql = MySqlContainer('mysql:5.6')
    mysql.start()

    def teardown():
        """Stops the containers after session
        """        
        mysql.stop()

    request.addfinalizer(teardown)

    return mysql
