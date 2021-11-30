from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from os import environ

ZOOKEEPER_CONNECT = "ZOOKEEPER_CONNECT"
KAFKA_ADVERTISED_HOST_NAME = "KAFKA_ADVERTISED_HOST_NAME"
ADVERTISED_HOST_NAME = "ADVERTISED_HOST_NAME"
KAFKA_ADVERTISED_PORT = "KAFKA_ADVERTISED_PORT"


class KafkaContainer(DockerContainer):
    """
    Kafka container.
    -------
    """
    ZOOKEEPER_CONNECT = environ.get(ZOOKEEPER_CONNECT, "zookeeper:2181")

    def __init__(self, zookeeperIp: str, image="debezium/kafka:1.7.1.Final", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to debezium/kafka:1.7.1.Final.
            ZOOKEEPER_CONNECT (str, optional): Kafka connect URL. Defaults to zookeeper:2181
        """
        super(KafkaContainer, self).__init__(image)
        self.with_bind_ports(9092, 9092)
        self.with_name("kafka")
        self.with_kwargs(
          hostname="kafka",
          extra_hosts={
            "zookeeper": zookeeperIp
          }
        )

        if 'ZOOKEEPER_CONNECT' in kwargs:
            self.ZOOKEEPER_CONNECT = kwargs['ZOOKEEPER_CONNECT']

    def start(self, timeout=60):
        """Starts the Kafka and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        self._configure()
        super().start()
        wait_for_logs(self, r'Recorded new controller', timeout=timeout)
        return self

    def _configure(self):
        """Configures the Kafka container
        """
        self.with_env(ZOOKEEPER_CONNECT, self.ZOOKEEPER_CONNECT)
        self.with_env(KAFKA_ADVERTISED_HOST_NAME, "kafka")
        self.with_env(ADVERTISED_HOST_NAME, "kafka")
        self.with_env(KAFKA_ADVERTISED_PORT, "9092")

    def get_kafka_ip(self) -> str:
        """Returns IP address for Kafka

        Returns:
            str: IP address for Kafka
        """
        return self.get_docker_client().bridge_ip(self._container.id)

    def get_kafka_url(self):
        """Returns Kafka's URL

        Returns:
            str: Kafka's URL
        """
        host = "kafka"
        port = 9092
        return f"{host}:{port}"
