import pytest
import os
from ..testcontainers.kafka import KafkaContainer
from ..testcontainers.zookeeper import ZookeeperContainer
from ..fixtures.zookeeper import *


@pytest.fixture(scope="session")
def kafka(request, zookeeper: ZookeeperContainer):
    """Kafka fixture

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        KafkaContainer: Reference to Kafka container
    """
    kafka = KafkaContainer(zookeeperIp=zookeeper.get_zookeeper_ip(), ZOOKEEPER_CONNECT=zookeeper.get_zookeeper_url())
    kafka.start()
    os.environ["KAFKA_BOOTSTRAP_SERVERS"] = kafka.get_kafka_url()

    def teardown():
        """Stops the containers after session
        """
        kafka.stop()

    request.addfinalizer(teardown)

    return kafka
