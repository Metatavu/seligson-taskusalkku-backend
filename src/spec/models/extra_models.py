# coding: utf-8

from typing import TypedDict, List


class RealmAccess(TypedDict):
    """Defines a access token realm access model."""

    roles: List[str]


class ResourceAccessAccount(TypedDict):
    """Defines a access token resource access account model."""

    roles: List[str]


class ResourceAccess(TypedDict):
    """Defines a access token resource access model."""

    account: ResourceAccessAccount


class TokenModel(TypedDict):
    """Defines an access token model."""

    exp: int
    iat: int
    jti: str
    iss: str
    aud: List[str]
    sub: str
    typ: str
    azp: str
    session_state: str
    acr: str
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    sid: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
