import pytest

from ..testcontainers.keycloak import KeycloakContainer
import os

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

    def teardown():
        """Stops the containers after session
        """
        keycloak.stop()

    request.addfinalizer(teardown)

    return keycloak
