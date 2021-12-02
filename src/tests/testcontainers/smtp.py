from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

class SmtpContainer(DockerContainer):
    """
    bytemark smtp container.
    -------
    """

    def __init__(self, image="marcopas/docker-mailslurper", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to "marcopas/docker-mailslurper:latest".
        """
        super(SmtpContainer, self).__init__(image)
        self.port_to_expose = 2500
        self.with_bind_ports(self.port_to_expose, self.port_to_expose)

    def start(self, timeout=60):
        """Starts the Keycloak and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        super().start()
        wait_for_logs(self, r'HTTP admin listener running', timeout=timeout)
        return self
