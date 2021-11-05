import requests
from ..testcontainers.keycloak import KeycloakContainer

class BearerAuth(requests.auth.AuthBase):
    """Bearer authentication strategy for requests
    """    

    def __init__(self, token):
        """Constructor

        Args:
            token (str): access token
        """        
        self.token = token

    def __call__(self, request: requests.Request):
        """applies authentication to the request

        Args:
            request (requests.Request): request

        Returns:
            requests.Request: altered request
        """        
        request.headers["authorization"] = "Bearer " + self.token
        return request

class AccessTokenProvider():
    """Authentication provider class for test purposes
    """    

    def __init__(self, keycloak: KeycloakContainer, realm: str, client_id: str, client_secret: str = None):
      """Constructor

      Args:
          keycloak (KeycloakContainer): Keycloak container reference
          realm (str): realm
          client_id (str): client id
          client_secret (str, optional): client secret. Defaults to None.
      """      
      self.keycloak = keycloak
      self.realm = realm
      self.client_id = client_id
      self.client_secret = client_secret

  
    def get_access_token(self, username: str, password: str) -> str:
        """Returns access token with given credentials

        Args:
            username (str): username
            password (str): password

        Returns:
            str: access token
        """        
        token_url = self.keycloak.get_oidc_token_url(realm=self.realm)
        data = {
          "client_id": self.client_id,
          "grant_type": "password",
          "username": username,
          "password": password
        }

        if (self.client_secret != None):
          data["client_secret"] = self.client_secret

        return requests.post(token_url, data = data).json()["access_token"]

