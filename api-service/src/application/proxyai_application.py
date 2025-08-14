from typing import Any
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Any
from ..domain.interfaces.request.tag_request import (
  CreateTag
)
from ..domain.enums.messages_enum import MessagesEnum
from ..infra.base.api_ai_proxy import ApiAiProxy
from ..usecase.ai_usecase import AiUseCase
from ..domain.enums.messages_enum import MessagesEnum

async def create_request(
  data: CreateTag,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  subpath: str
) -> Any:
  return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }
