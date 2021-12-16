# coding: utf-8

import logging
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from spec.models.extra_models import TokenModel
from auth.oidc import Oidc

logger = logging.getLogger(__name__)

bearer_auth = HTTPBearer()


def get_token_bearer(credentials: HTTPAuthorizationCredentials = Depends(bearer_auth)) -> TokenModel:
    """Returns

    Args:
        credentials (HTTPAuthorizationCredentials, optional): Credentials from the HTTP Request. Defaults to Depends(bearer_auth).

    Raises:
        HTTPException: thrown on authorization errors

    Returns:
        TokenModel: Returns access token
    """

    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")

    oidc_auth_server_url = os.environ["OIDC_AUTH_SERVER_URL"]
    if not oidc_auth_server_url:
        raise HTTPException(status_code=500, detail="Missing OIDC_AUTH_SERVER_URL env variable")

    oidc_audience = os.environ["OIDC_AUDIENCE"]
    if not oidc_audience:
        raise HTTPException(status_code=500, detail="Missing OIDC_AUDIENCE env variable")

    oidc = Oidc(oidc_auth_server_url=oidc_auth_server_url)

    token = oidc.decode_jwt_token(token=credentials.credentials, audience=oidc_audience)
    if not token:
        raise HTTPException(status_code=403, detail="Forbidden")

    return token
