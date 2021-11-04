import pytest

from ..auth.auth import AccessTokenProvider, BearerAuth
from ..testcontainers.keycloak import KeycloakContainer
from ...app.main import app
from ..fixtures.keycloak import *

@pytest.fixture()
def user_1_token(keycloak: KeycloakContainer) -> str:
    """Fixture for providing access token for user 1

    Args:
        keycloak (KeycloakContainer): reference to Keycloak container

    Returns:
        str: access token
    """    

    access_token_provider = AccessTokenProvider(keycloak = keycloak, realm="seligson", client_id="ui")
    return access_token_provider.get_access_token(username="user1", password="test") #NOSONAR

@pytest.fixture()
def user_1_auth(user_1_token: str) -> BearerAuth:
    """Fixture for providing auth for user 1

    Args:
        user_1_token (str): user 1 access token

    Returns:
        BearerAuth: authentication
    """    
    
    return BearerAuth(token=user_1_token)
