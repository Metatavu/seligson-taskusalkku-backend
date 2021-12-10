import os
from uuid import UUID

from keycloak import KeycloakAdmin
import logging

logger = logging.getLogger(__name__)


class KeycloakAdminAccess:

    def __init__(self):
        self.KEYCLOAK_ADMIN_USER = os.environ["KEYCLOAK_ADMIN_USER"]
        self.KEYCLOAK_ADMIN_PASSWORD = os.environ["KEYCLOAK_ADMIN_PASSWORD"]
        self.KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"]
        self.KEYCLOAK_ADMIN_CLIENT_SECRET = os.environ["KEYCLOAK_ADMIN_CLIENT_SECRET"]
        self.KEYCLOAK_URL = os.environ["KEYCLOAK_URL"]
        self.KEYCLOAK_ADMIN_CLIENT_ID = os.environ["KEYCLOAK_ADMIN_CLIENT_ID"]

    def get_user_ssn(self, user_id: str) -> str:
        admin = self.get_admin()
        user = admin.get_user(user_id)
        return user.get("attributes").get("SSN")[0]

    def get_admin(self):
        admin = KeycloakAdmin(server_url=self.KEYCLOAK_URL,
                              username=self.KEYCLOAK_ADMIN_USER,
                              password=self.KEYCLOAK_ADMIN_PASSWORD,
                              realm_name=self.KEYCLOAK_REALM,
                              client_id=self.KEYCLOAK_ADMIN_CLIENT_ID,
                              client_secret_key=self.KEYCLOAK_ADMIN_CLIENT_SECRET,
                              verify=False)
        return admin
