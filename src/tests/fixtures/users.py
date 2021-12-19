from ..auth.auth import AccessTokenProvider, BearerAuth
from ..fixtures.keycloak import *
from ..testcontainers.keycloak import KeycloakContainer


@pytest.fixture()
def user_1_auth(keycloak: KeycloakContainer) -> BearerAuth:
    """Fixture for providing auth for user 1

    Args:
        keycloak (str): Keycloak container

    Returns:
        BearerAuth: authentication
    """

    access_token_provider = AccessTokenProvider(keycloak=keycloak, realm="seligson", client_id="ui")
    token = access_token_provider.get_access_token(username="user1", password="test")  # NOSONAR
    return BearerAuth(token=token)


@pytest.fixture()
def user_2_auth(keycloak: KeycloakContainer) -> BearerAuth:
    """Fixture for providing auth for user 2

    Args:
        keycloak (str): Keycloak container

    Returns:
        BearerAuth: authentication
    """

    access_token_provider = AccessTokenProvider(keycloak=keycloak, realm="seligson", client_id="ui")
    token = access_token_provider.get_access_token(username="user2", password="test")  # NOSONAR
    return BearerAuth(token=token)


@pytest.fixture()
def user_3_auth(keycloak: KeycloakContainer) -> BearerAuth:
    """Fixture for providing auth for user 3

    Args:
        keycloak (str): Keycloak container

    Returns:
        BearerAuth: authentication
    """

    access_token_provider = AccessTokenProvider(keycloak=keycloak, realm="seligson", client_id="ui")
    token = access_token_provider.get_access_token(username="user3", password="test")  # NOSONAR
    return BearerAuth(token=token)


@pytest.fixture()
def anonymous_auth(keycloak: KeycloakContainer) -> BearerAuth:
    """Fixture for providing auth for anonymous user

    Args:
        keycloak (str): Keycloak container

    Returns:
        BearerAuth: authentication
    """

    access_token_provider = AccessTokenProvider(keycloak=keycloak, realm="seligson", client_id="ui")
    token = access_token_provider.get_access_token(username="anonymous", password="test")  # NOSONAR
    return BearerAuth(token=token)
