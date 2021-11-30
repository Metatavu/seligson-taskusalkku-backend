from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

KAFKA_BOOTSTRAP_SERVERS = "KAFKA_BOOTSTRAP_SERVERS"

class SyncContainer(DockerContainer):
    """
    Sync container.
    -------
    """

    def __init__(self, kafkaIp: str, image="seligson-sync", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to seligson-sync
        """
        super(SyncContainer, self).__init__(image)

        self.with_kwargs(
          extra_hosts={
            "kafka": kafkaIp
          }
        )

    def start(self, timeout=60):
        """Starts the Sync and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        self._configure()
        super().start()
        wait_for_logs(self, r'Started synchronizing.', timeout=timeout)
        return self

    def _configure(self):
        """Configures the Kafka container
        """
        self.with_env(KAFKA_BOOTSTRAP_SERVERS, "kafka:9092")