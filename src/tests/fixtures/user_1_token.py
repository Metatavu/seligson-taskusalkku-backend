import pytest
from starlette.testclient import TestClient

from ..auth.auth import Auth
from ..testcontainers.keycloak import KeycloakContainer
from ...app.main import app
from ..fixtures.keycloak import keycloak

@pytest.fixture()
def user_1_token(keycloak: KeycloakContainer) -> str:
    """Fixture for providing access token for user 1

    Args:
        keycloak (KeycloakContainer): [description]

    Returns:
        str: access token
    """    

    auth = Auth(keycloak = keycloak, realm="seligson", client_id="ui")
    return auth.get_access_token(username="user1", password="test")
