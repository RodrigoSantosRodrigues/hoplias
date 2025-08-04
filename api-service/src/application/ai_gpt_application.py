from typing import Any
from fastapi import Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Any, Dict

from ..infra.base.rpc_proxy import RpcProxy
from ..infra.base.ai_gpt_client import AiGptClient
from ..domain.enums.messages_enum import MessagesEnum

async def create_request(
  data: dict,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  subpath: str
) -> Dict:
  rpc_proxy = RpcProxy(request.app.config)
  ai_gpt_client = AiGptClient(request.app.config)
  response_chat = None

  endpoints_map = rpc_proxy.get_endpoints()
  endpoint_url = endpoints_map.get(subpath)
  if not endpoint_url:
    return {
    'success': False,
    'message': MessagesEnum.NOT_FOUND
  }

  response = await rpc_proxy.api_proxy(endpoint_url, data)
  if not response:
    return {
    'success': False,
    'message': MessagesEnum.ERROR_IN_REQUEST_GATEWAY
  }

  if data.get('just_chat'):
    response_chat = ai_gpt_client.api_request()

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'chat_helper': response_chat,
    'data': response
  }
