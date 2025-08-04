from typing import Any
from fastapi import Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Any, Dict

from ..domain.interfaces.request.kariotype_request import CreateKariotype
from ..infra.base.rpc_proxy import RpcProxy
from ..domain.enums.messages_enum import MessagesEnum
from ..usecase.analyse_chromosomes_usecase import AnalyseChromosomes

async def create_request(
  data: CreateKariotype,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  subpath: str
) -> Dict:
  rpc_proxy = RpcProxy(request.app.config)

  endpoints_map = rpc_proxy.get_endpoints()
  endpoint_url = endpoints_map.get(subpath)
  if not endpoint_url:
    return {
    'success': False,
    'message': MessagesEnum.NOT_FOUND
  }

  analyze_chromosomes = AnalyseChromosomes(
    data=data,
    request=request, 
    db=db,
    auth=auth,
    endpoint_url=endpoint_url
  )

  response = await analyze_chromosomes.orchestrator()

  if not response:
    return {
    'success': False,
    'message': MessagesEnum.ERROR_IN_REQUEST_GATEWAY
  }
 
  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': response
  }
