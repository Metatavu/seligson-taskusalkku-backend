import pytest

from ..testcontainers.zookeeper import ZookeeperContainer


@pytest.fixture(scope="session")
def zookeeper(request):
    """Zookeeper fixture

    Returns:
        ZookeeperContainer: Reference to Zookeeper container
    """
    zookeeper = ZookeeperContainer()

    zookeeper.start()

    def teardown():
        """Stops the containers after session"""
        zookeeper.stop()

    request.addfinalizer(teardown)

    return zookeeper
