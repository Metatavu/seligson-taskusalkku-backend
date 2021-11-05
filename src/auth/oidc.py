import requests
import jwt
import logging

from cryptography.x509.base import Certificate
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class Oidc():
  """OIDC helper class
  """

  def __init__(self, oidc_auth_server_url: str):
    """Constructor

    Args:
        oidc_auth_server_url (str): OIDC Server URL
    """
    self.oidc_auth_server_url = oidc_auth_server_url

  def decode_jwt_token(self, token: str, audience: str) -> dict:
    """Decodes JWT token and verify's it's signature.

    Args:
        token (str): JWT token
        audience (str): token audience

    Returns:
        dict: parsed token
    """

    if (not token):
      logger.warning("No token provided")
      return None

    jwt_header = jwt.get_unverified_header(token)
    if (not jwt_header):
      logger.warning("Could not parse JWT header")
      return None
      
    kid = jwt_header["kid"]
    if (not kid):
      logger.warning("Could not resolve kid from JWT header")
      return None
      
    oidc_config = self.get_oidc_config(self.oidc_auth_server_url + "/.well-known/openid-configuration")
    token_endpoint_auth_signing_alg_values_supported = oidc_config["token_endpoint_auth_signing_alg_values_supported"]
    issuer = oidc_config["issuer"]
    jwks_uri = oidc_config["jwks_uri"]
    if (not jwks_uri):
      logger.warning("Could not resolve jwks_uri from OIDC config")
      return None
      
    jwks = self.get_jwks(jwks_uri = jwks_uri)
    if (not jwks):
      logger.warning("Could not resolve JWKS")
      return None
      
    certificate = self.get_certificate(jwks = jwks, kid = kid)
    if (not certificate):
      logger.warning("Could not resolve certificate")
      return None
      
    return jwt.decode(token, certificate.public_key(), issuer=issuer, audience=audience, algorithms=token_endpoint_auth_signing_alg_values_supported)

  def get_certificate(self, jwks: dict, kid: str) -> Certificate:
    """Returns certificate for given kid using JWKS object as source

    Args:
        jwks (dict): JWKS object
        kid (str): kid

    Returns:
        Certificate: certificate
    """
    keys = jwks["keys"]
    key = next(key for key in keys if key["kid"] == kid)
    x5c = key["x5c"][0]
    certificate = '-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----'.format(x5c)
    return load_pem_x509_certificate(certificate.encode(), default_backend())
  
  def get_oidc_config(self, oidc_config_url: str) -> dict:
    """Returns OIDC config from config URL

    Args:
        oidc_config_url (str): OIDC config URL

    Returns:
        dict: JSON object
    """
    return requests.get(oidc_config_url).json()

  def get_jwks(self, jwks_uri: str) -> dict:
    """Returns JWKS object from given URI

    Args:
        jwks_uri (str): JWKS URI

    Returns:
        dict: JSON object
    """    
    return requests.get(jwks_uri).json()
