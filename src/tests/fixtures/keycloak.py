import pytest

from ..testcontainers.keycloak import KeycloakContainer
import os
import time
keycloak_import_file = os.path.join(os.path.dirname(__file__),
                                    '..',
                                    'data',
                                    'kc.json')


@pytest.fixture(scope="session")
def keycloak(request):
    """Keycloak fixture

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        KeycloakContainer: Reference to Keycloak container
    """
    keycloak = KeycloakContainer("quay.io/keycloak/keycloak:15.0.2",
                                 KEYCLOAK_IMPORT=keycloak_import_file
                                 )

    keycloak.start()
    keycloak_url = keycloak.get_keycloak_url()
    os.environ["OIDC_AUTH_SERVER_URL"] = f"{keycloak_url}/realms/seligson"
    os.environ["OIDC_AUDIENCE"] = "api"
    os.environ["KEYCLOAK_REALM"] = "seligson"
    os.environ["KEYCLOAK_URL"] = f"{keycloak_url}/"
    os.environ["KEYCLOAK_ADMIN_CLIENT_SECRET"] = "b80e7b4a-ceb1-465b-b6e2-7e01b8de7484"
    os.environ["KEYCLOAK_ADMIN_CLIENT_ID"] = "api"
    os.environ["KEYCLOAK_ADMIN_PASSWORD"] = "test"
    os.environ["KEYCLOAK_ADMIN_USER"] = "api-admin"

    def teardown():
        """Stops the containers after session
        """
        keycloak.stop()

    request.addfinalizer(teardown)

    return keycloak
