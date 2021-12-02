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
    os.environ["MAIL_USERNAME"] = ""
    os.environ["MAIL_PASSWORD"] = ""
    os.environ["MAIL_FROM"] = "test@example.com"
    os.environ["MAIL_TO"] = "test2@example.com"
    os.environ["MAIL_PORT"] = smtp.get_smtp_port()
    os.environ["MAIL_SERVER"] = smtp.get_smtp_host()
    os.environ["MAIL_TLS"] = "False"
    os.environ["MAIL_SSL"] = "False"

    def teardown():
        """Stops the containers after session
        """
        smtp.stop()

    request.addfinalizer(teardown)

    return smtp
