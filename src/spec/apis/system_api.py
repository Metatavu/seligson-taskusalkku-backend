# coding: utf-8

from typing import Dict, List  # noqa: F401
from abc import ABC, abstractmethod

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from spec.models.extra_models import TokenModel  # noqa: F401


router = APIRouter()
router = InferringRouter()


@cbv(router)
class SystemApiSpec(ABC):
    
    @abstractmethod
    async def ping(
        self,
    ) -> str:
        ...

    @router.get(
        "/v1/system/ping",
        responses={
            200: {"model": str, "description": "Pong"},
        },
        tags=["System"],
        summary="Replies with pong",
    )
    async def ping_spec(
        self,
    ) -> str:
        """Replies ping with pong"""
        return await self.ping(
            
        )
