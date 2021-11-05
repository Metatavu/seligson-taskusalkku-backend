# coding: utf-8

from fastapi_utils.cbv import cbv
from spec.apis.system_api import SystemApiSpec, router as SystemApiRouter


@cbv(SystemApiRouter)
class SystemApiImpl(SystemApiSpec):

    async def ping(self) -> str:
        return "pong"
