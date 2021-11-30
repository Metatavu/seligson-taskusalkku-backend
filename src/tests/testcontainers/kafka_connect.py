from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from os import environ


BOOTSTRAP_SERVERS = "BOOTSTRAP_SERVERS"
GROUP_ID = "GROUP_ID"
CONFIG_STORAGE_TOPIC = "CONFIG_STORAGE_TOPIC"
OFFSET_STORAGE_TOPIC = "OFFSET_STORAGE_TOPIC"
STATUS_STORAGE_TOPIC = "STATUS_STORAGE_TOPIC"


class KafkaConnectContainer(DockerContainer):
    """
    Kafka Connect container.
    """
    BOOTSTRAP_SERVERS = None
    GROUP_ID = environ.get(GROUP_ID, "test")

    def __init__(self, kafkaIp: str, image="debezium/connect:1.7.1.Final", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to "debezium/connect:1.7.1.Final".
            BOOTSTRAP_SERVERS (str, optional): Kafka bootstap servers.
            GROUP_ID (str, optional): Group id. Defaults to test
        """
        super(KafkaConnectContainer, self).__init__(image)
        self.with_exposed_ports(8083)

        self.with_kwargs(
          extra_hosts={
            "kafka": kafkaIp
          }
        )

        if 'BOOTSTRAP_SERVERS' in kwargs:
            self.BOOTSTRAP_SERVERS = kwargs['BOOTSTRAP_SERVERS']
        if 'GROUP_ID' in kwargs:
            self.GROUP_ID = kwargs['GROUP_ID']

    def start(self, timeout=60):
        """Starts the Kafka Connect and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        self._configure()
        super().start()
        wait_for_logs(self, r'Kafka Connect started', timeout=timeout)
        return self

    def _configure(self):
        """Configures the Kafka Connect container"""
        self.with_env(BOOTSTRAP_SERVERS, self.BOOTSTRAP_SERVERS)
        self.with_env(GROUP_ID, self.GROUP_ID)
        self.with_env(CONFIG_STORAGE_TOPIC, "my_connect_configs")
        self.with_env(OFFSET_STORAGE_TOPIC, "my_connect_offsets")
        self.with_env(STATUS_STORAGE_TOPIC, "my_connect_statuses")

    def get_kafka_connect_url(self):
        """Returns Kafka Connect's URL

        Returns:
            str: Kafka Connect's URL
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(8083)
        return f"http://{host}:{port}"
