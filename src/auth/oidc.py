import requests
import jwt
import logging

from cryptography.x509.base import Certificate
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from typing import Union, List

from jwt import InvalidIssuedAtError

logger = logging.getLogger(__name__)


class Oidc:
    """OIDC helper class"""

    def __init__(self, issuers: List[str]):
        """Constructor

    Args:
        issuers (str): allowed issuers
    """
        self.issuers = issuers

    def decode_jwt_token(self, token: str, audience: str) -> Union[dict, None]:
        """Decodes JWT token and verifies its signature.

        Args:
            token (str): JWT token
            audience (str): token audience

        Returns:
            dict: parsed token
        """

        if not token:
            logger.warning("No token provided")
            return None

        jwt_header = jwt.get_unverified_header(token)
        if not jwt_header:
            logger.warning("Could not parse JWT header")
            return None

        kid = jwt_header.get("kid", None)
        if not kid:
            logger.warning("Could not resolve kid from JWT header")
            return None

        for issuer in self.issuers:
            logger.info(f"Parsing token with issuer {issuer}")

            try:
                result = self.try_decode_with_issuer(
                    issuer=issuer,
                    token=token,
                    audience=audience,
                    kid=kid
                )

                if result:
                    return result

            except InvalidIssuedAtError:
                logger.warning(f"Could parse token with issuer {issuer}")
                pass

        return None

    def try_decode_with_issuer(self, issuer: str, token: str, audience: str, kid: str):
        """
        Tries to decode token using given issuer

        Args:
            issuer: issuer
            token: token
            audience: audience
            kid: kid

        Returns:
            Decoded token or None if decoding fails
        """
        oidc_config = self.get_oidc_config(issuer + "/.well-known/openid-configuration")
        token_endpoint_auth_signing_alg_values_supported = oidc_config[
            "token_endpoint_auth_signing_alg_values_supported"
        ]

        issuer = oidc_config.get("issuer", "")
        jwks_uri = oidc_config.get("jwks_uri", "")
        if not jwks_uri:
            logger.warning("Could not resolve jwks_uri from OIDC config")
            return None

        jwks = self.get_jwks(jwks_uri=jwks_uri)
        if not jwks:
            logger.warning("Could not resolve JWKS")
            return None

        certificate = self.get_certificate(jwks=jwks, kid=kid)
        if not certificate:
            logger.warning("Could not resolve certificate")
            return None

        return jwt.decode(
            jwt=token,
            key=certificate.public_key(),
            issuer=issuer,
            audience=audience,
            algorithms=token_endpoint_auth_signing_alg_values_supported
        )

    @staticmethod
    def get_certificate(jwks: dict, kid: str) -> Certificate:
        """Returns certificate for given kid using JWKS object as source

    Args:
        jwks (dict): JWKS object
        kid (str): kid

    Returns:
        Certificate: certificate
    """
        keys = jwks["keys"]
        key = next(key for key in keys if key.get("kid", "") == kid)
        x5c = key.get("x5c", [""])[0]
        certificate = '-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----'.format(x5c)
        return load_pem_x509_certificate(certificate.encode(), default_backend())

    @staticmethod
    def get_oidc_config(oidc_config_url: str) -> dict:
        """Returns OIDC config from config URL

    Args:
        oidc_config_url (str): OIDC config URL

    Returns:
        dict: JSON object
    """
        return requests.get(oidc_config_url).json()

    @staticmethod
    def get_jwks(jwks_uri: str) -> dict:
        """Returns JWKS object from given URI

    Args:
        jwks_uri (str): JWKS URI

    Returns:
        dict: JSON object
    """    
        return requests.get(jwks_uri).json()
