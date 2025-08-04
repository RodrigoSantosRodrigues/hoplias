import datetime
from typing import Any, Dict
from fastapi import APIRouter, Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.notification_application import (
  get_by_search,
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.get("/search", response_model=Dict)
async def get_list(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
  order_by: str = None,
  search: str = None,
  page: int = 1,
  page_size: int = 10
) -> Any:
  """
    Get list.
  """
  data = await get_by_search(
    request,
    db,
    auth,
    team_id,
    order_by,
    search,
    page,
    page_size
  )
  return custom_response(
    jsonable_encoder(jsonable_encoder(data)),
    StatusCode.HTTP_OK
  )
