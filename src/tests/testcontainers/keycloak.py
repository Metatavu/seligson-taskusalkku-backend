from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from os import environ


KEYCLOAK_USER = "KEYCLOAK_USER"
KEYCLOAK_PASSWORD = "KEYCLOAK_PASSWORD"
KEYCLOAK_IMPORT = "KEYCLOAK_IMPORT"

realm_import_file = "/tmp/kc.json"  # NOSONAR


class KeycloakContainer(DockerContainer):
    """
    Keycloak container.
    -------
    """
    KEYCLOAK_USER = environ.get(KEYCLOAK_USER, "admin")
    KEYCLOAK_PASSWORD = environ.get(KEYCLOAK_PASSWORD, "admin")
    KEYCLOAK_IMPORT = environ.get(KEYCLOAK_IMPORT)

    def __init__(self, image="quay.io/keycloak/keycloak:latest", **kwargs):
        """Constructor

        Args:
            image (str, optional): Used Docker image. Defaults to "quay.io/keycloak/keycloak:latest".
            KEYCLOAK_USER (str, optional): Keycloak admin user. Defaults to admin
            KEYCLOAK_PASSWORD (str, optional): Keycloak admin password. Defaults to admin
            KEYCLOAK_IMPORT (str, optional): Path to Keycloak realm import file.
        """
        super(KeycloakContainer, self).__init__(image)
        self.port_to_expose = 8080
        self.with_exposed_ports(self.port_to_expose)
        if 'KEYCLOAK_USER' in kwargs:
            self.KEYCLOAK_USER = kwargs['KEYCLOAK_USER']
        if 'KEYCLOAK_PASSWORD' in kwargs:
            self.KEYCLOAK_PASSWORD = kwargs['KEYCLOAK_PASSWORD']
        if 'KEYCLOAK_IMPORT' in kwargs:
            self.KEYCLOAK_IMPORT = kwargs['KEYCLOAK_IMPORT']

    def start(self, timeout=60):
        """Starts the Keycloak and waits for it to be ready.

        Args:
            timeout (int, optional): Timeout for container to be ready. Defaults to 60.
        """
        self._configure()
        super().start()
        wait_for_logs(self, r'Resuming server\n', timeout=timeout)
        return self

    def get_keycloak_url(self):
        """Returns Keycloak's URL

        Returns:
            str: Keycloak's URL
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(8080)
        return "http://" + host + ":" + port + "/auth"  # NOSONAR

    def get_oidc_token_url(self, realm):
        """Returns access token URL for given realm

        Args:
            realm (str): realm

        Returns:
            str: Access token URL
        """
        url = self.get_keycloak_url()
        return f"{url}/realms/{realm}/protocol/openid-connect/token"

    def _configure(self):
        """Configures the Keycloak container
        """
        self.with_env(KEYCLOAK_USER, self.KEYCLOAK_USER)
        self.with_env(KEYCLOAK_PASSWORD, self.KEYCLOAK_PASSWORD)

        if self.KEYCLOAK_IMPORT:
            self.with_volume_mapping(
              self.KEYCLOAK_IMPORT,
              realm_import_file
            )

            self.with_env(
              KEYCLOAK_IMPORT,
              realm_import_file
            )
