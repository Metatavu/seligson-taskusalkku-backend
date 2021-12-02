import pytest

from ..testcontainers.smtp import SmtpContainer
import os


@pytest.fixture(scope="session")
def smtp(request):
    """smtp fixture

    Args:
        request (FixtureRequest): A fixture request object

    Returns:
        SmtpContainer: Reference to smtp container
    """
    smtp = SmtpContainer()

    smtp.start()

    def teardown():
        """Stops the containers after session
        """
        smtp.stop()

    request.addfinalizer(teardown)

    return smtp
