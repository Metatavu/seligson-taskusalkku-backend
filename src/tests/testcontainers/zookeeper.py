from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class ZookeeperContainer(DockerContainer):
    """
    Zookeeper container.
    -------
    """

    def __init__(self, image="debezium/zookeeper:1.7.1.Final", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to debezium/zookeeper:1.7.1.Final.
        """
        super(ZookeeperContainer, self).__init__(image)
        self.with_bind_ports(2181, 2181)
        self.with_bind_ports(2888, 2888)
        self.with_bind_ports(3888, 3888)
        self.with_name("zookeper")
        self.with_kwargs(
          hostname="zookeper"
        )

    def start(self, timeout=60):
        """Starts the Zookeeper and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        super().start()
        wait_for_logs(self, r'binding to port', timeout=timeout)
        return self

    def get_zookeeper_url(self):
        """Returns Zookeeper's URL

        Returns:
            str: Zookeeper's URL
        """
        host = "zookeeper"
        port = 2181
        return f"{host}:{port}"

    def get_zookeeper_ip(self) -> str:
        
        return self.get_docker_client().bridge_ip(self._container.id)
