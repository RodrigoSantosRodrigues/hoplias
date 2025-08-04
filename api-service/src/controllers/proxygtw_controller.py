from typing import Any, Dict
from fastapi import APIRouter, Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder

from ..domain.interfaces.request.kariotype_request import CreateKariotype
from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.proxygtw_application import (
  create_request,
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post('/{subpath:path}', response_model=Dict)
async def create(
  data: CreateKariotype,
  subpath: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create request.
  """
  response = await create_request(data, request, db, auth, subpath)
  if not response.get('success'):
    return custom_response(
      jsonable_encoder(response),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(response),
    StatusCode.HTTP_OK
  )
