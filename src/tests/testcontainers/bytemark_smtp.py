from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from os import environ

# bytemark smtp env
RELAY_HOST = "RELAY_HOST"
RELAY_USERNAME = "RELAY_USERNAME"
RELAY_PASSWORD = "RELAY_PASSWORD"

# app env
MAIL_SERVER = "MAIL_SERVER"
MAIL_USERNAME = "MAIL_USERNAME"
MAIL_PASSWORD = "MAIL_PASSWORD"


class BytemarkSmtpContainer(DockerContainer):
    """
    bytemark smtp container.
    -------
    """
    MAIL_USERNAME = environ.get(MAIL_USERNAME)
    MAIL_PASSWORD = environ.get(MAIL_PASSWORD)
    MAIL_SERVER = environ.get(MAIL_SERVER)

    def __init__(self, image="bytemark/smtp:latest", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to "bytemark/smtp:latest".
            MAIL_USERNAME (str, optional): The username to authenticate with the remote SMTP server.
            MAIL_PASSWORD (str, optional): The password to authenticate with the remote SMTP server.
            MAIL_SERVER (str, optional):  The remote SMTP server address to use.
        """
        super(BytemarkSmtpContainer, self).__init__(image)
        self.port_to_expose = 587
        self.with_exposed_ports(self.port_to_expose)
        if MAIL_SERVER in kwargs:
            self.MAIL_SERVER = kwargs[MAIL_SERVER]
        if MAIL_USERNAME in kwargs:
            self.MAIL_USERNAME = kwargs[MAIL_USERNAME]
        if MAIL_PASSWORD in kwargs:
            self.MAIL_PASSWORD = kwargs[MAIL_PASSWORD]

    def start(self, timeout=60):
        """Starts the Keycloak and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        self._configure()
        super().start()
        wait_for_logs(self, r'listening for SMTP on port', timeout=timeout)
        return self

    def _configure(self):
        """Configures the smtp container
        """
        self.with_env(RELAY_HOST, self.MAIL_SERVER)
        self.with_env(RELAY_USERNAME, self.MAIL_USERNAME)
        self.with_env(RELAY_PASSWORD, self.MAIL_PASSWORD)
