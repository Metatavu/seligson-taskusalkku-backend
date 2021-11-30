import pytest

from tests.testcontainers.kafka_connect import KafkaConnectContainer
from tests.testcontainers.kafka import KafkaContainer

from ..testcontainers.sync import SyncContainer


@pytest.fixture(scope="session")
def sync(request, kafka: KafkaContainer, kafka_connect: KafkaConnectContainer):
    """Sync fixture

    Returns:
        SyncContainer: Reference to Sync container
    """
    sync = SyncContainer(kafkaIp=kafka.get_kafka_ip())

    sync.start()

    def teardown():
        """Stops the containers after session"""
        sync.stop()

    request.addfinalizer(teardown)

    return sync
