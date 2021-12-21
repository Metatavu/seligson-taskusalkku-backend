from typing import List
from admin.keycloak_admin import KeycloakAdminAccess
from spec.models.extra_models import TokenModel


class AuthUtils:
    """
    Authentication related utils
    """

    @staticmethod
    def get_user_ssn(token_bearer: TokenModel) -> str:
        """
        Retrieves SSN for user from Keycloak

        Args:
            token_bearer (TokenModel): user access token

        Returns:
            SSN or None if not found
        """
        keycloak_admin_access = KeycloakAdminAccess()
        return keycloak_admin_access.get_user_ssn(token_bearer.get("sub", ""))

    @staticmethod
    def get_user_roles(token_bearer: TokenModel) -> List[str]:
        """
        Returns roles from access token
        Args:
            token_bearer: logged user access token

        Returns:
            roles from access token
        """
        realm_access = token_bearer.get("realm_access", None)
        if realm_access is None:
            return []

        return realm_access.get("roles", [])

    @staticmethod
    def has_user_role(token_bearer: TokenModel) -> bool:
        """
        Returns whether logged user has user role
        Args:
            token_bearer: logged user access token

        Returns:
            whether logged user has user role
        """
        roles = AuthUtils.get_user_roles(token_bearer=token_bearer)
        return "user" in roles
