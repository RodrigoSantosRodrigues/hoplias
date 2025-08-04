import uuid
import logging
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict
import asyncio

from ..domain.interfaces.request.tag_request import CreateTag
from ..infra.base.api_ai_proxy import ApiAiProxy
from ..helpers.mappers import RoutePathApiAi

class AiUseCase:
  def __init__(
      self,
      data: CreateTag,
      request: Request,
      db: AsyncIOMotorCollection,
      auth: str, 
      endpoint_url: str
    ):
    self.data = data
    self.request = request
    self.__db = db
    self.__auth = auth
    self.__endpoint_url = endpoint_url
    self.api_ai_proxy = ApiAiProxy(self.request.app.config)
 
  async def orchestrator(self) -> any:
    if self.__endpoint_url == RoutePathApiAi.CATEGORY_SUGESTION:
      return await self.create_tag()

  async def create_tag(self) -> Dict:
    response = await self.api_ai_proxy.api_proxy(self.__endpoint_url, self.data.dict())

    return response
