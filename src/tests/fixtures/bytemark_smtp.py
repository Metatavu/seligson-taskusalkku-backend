import pytest

from ..testcontainers.bytemark_smtp import BytemarkSmtpContainer
import os


@pytest.fixture(scope="session")
def bytemark_smtp(request):
    """bytemark smtp fixture

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        KeycloakContainer: Reference to Keycloak container
    """
    smtp = BytemarkSmtpContainer()

    smtp.start()

    def teardown():
        """Stops the containers after session
        """
        smtp.stop()

    request.addfinalizer(teardown)

    return smtp
