import pytest

from tests.testcontainers.kafka_connect import KafkaConnectContainer
from tests.testcontainers.kafka import KafkaContainer

from ..testcontainers.sync import SyncContainer
from testcontainers.mysql import MySqlContainer


@pytest.fixture(scope="session")
def sync(request, kafka: KafkaContainer, backend_mysql: MySqlContainer, kafka_connect: KafkaConnectContainer):
    """Sync fixture

    Returns:
        SyncContainer: Reference to Sync container
    """
    mysql_host = backend_mysql.get_docker_client().bridge_ip(backend_mysql._container.id)
    database_url = f"mysql+pymysql://test:test@{mysql_host}:3306/test"

    sync = SyncContainer(kafka_ip=kafka.get_kafka_ip(), database_url=database_url)

    sync.start()

    def teardown():
        """Stops the containers after session"""
        sync.stop()

    request.addfinalizer(teardown)

    return sync
