from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os


class Mailer:
    """
    Mailer
    """

    @staticmethod
    def send_mail(message: MessageSchema):
        """
        Sends an e-mail
        Args:
            message: message
        """
        mail_username = os.environ["MAIL_USERNAME"]
        mail_password = os.environ["MAIL_PASSWORD"]
        use_credentials = bool(mail_username) and bool(mail_password)
        validate_certs = use_credentials

        email_conf = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=os.environ["MAIL_FROM"],
            MAIL_PORT=os.environ["MAIL_PORT"],
            MAIL_SERVER=os.environ["MAIL_SERVER"],
            MAIL_TLS=eval(os.environ["MAIL_TLS"]),
            MAIL_SSL=eval(os.environ["MAIL_SSL"]),
            USE_CREDENTIALS=use_credentials,
            VALIDATE_CERTS=validate_certs
        )

        fast_mail = FastMail(email_conf)
        return fast_mail.send(message)