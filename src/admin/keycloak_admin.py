import os
from typing import Optional

from keycloak import KeycloakAdmin
import logging

logger = logging.getLogger(__name__)


class KeycloakAdminAccess:
    """
    Keycloak admin client
    """

    def __init__(self):
        self.KEYCLOAK_ADMIN_USER = os.environ["KEYCLOAK_ADMIN_USER"]
        self.KEYCLOAK_ADMIN_PASSWORD = os.environ["KEYCLOAK_ADMIN_PASSWORD"]
        self.KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"]
        self.KEYCLOAK_ADMIN_CLIENT_SECRET = os.environ["KEYCLOAK_ADMIN_CLIENT_SECRET"]
        self.KEYCLOAK_URL = os.environ["KEYCLOAK_URL"]
        self.KEYCLOAK_ADMIN_CLIENT_ID = os.environ["KEYCLOAK_ADMIN_CLIENT_ID"]

    def get_user_ssn(self, user_id: str) -> Optional[str]:
        """
        Retrieves SSN for user_id from Keycloak

        Args:
            user_id (str): user id

        Returns:
            SSN or None if not found
        """
        admin = self.get_admin()
        user = admin.get_user(user_id)
        attributes = user.get("attributes", None)

        ssn_attribute = None
        if attributes is not None:
            ssn_attribute = attributes.get("SSN", None)

        if ssn_attribute is not None and len(ssn_attribute) == 1:
            return ssn_attribute[0]

        return None

    def get_admin(self):
        """
        Returns Keycloak admin client

        Returns: Keycloak admin client
        """
        admin = KeycloakAdmin(server_url=self.KEYCLOAK_URL,
                              username=self.KEYCLOAK_ADMIN_USER,
                              password=self.KEYCLOAK_ADMIN_PASSWORD,
                              realm_name=self.KEYCLOAK_REALM,
                              client_id=self.KEYCLOAK_ADMIN_CLIENT_ID,
                              client_secret_key=self.KEYCLOAK_ADMIN_CLIENT_SECRET,
                              verify=False)
        return admin
