from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.ideogram_application import (
  create_ideogram,
  get_ideogram_by_id,
  update_ideogram,
  get_all_ideogram,
  remove_ideogram
)
from ..domain.interfaces.request.ideogram_request import (
  CreateIdeogramDto,
  UpdateIdeogramDto
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateIdeogramDto,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """'
    Create.
  """
  ideogram = await create_ideogram(data, request, db, auth)
  if not ideogram.get('success'):
    return custom_response(
      jsonable_encoder(ideogram),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(ideogram),
    StatusCode.HTTP_OK
  )


@router.get("/search", response_model=dict)
async def query_by_search(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
  order_by: str = None,
  search: str = None,
  page: int = 1,
  page_size: int = 10,
  start_date: str = None,
  end_date: str = None,
) -> Any:
  """
    Get.
  """
  ideograms = await get_all_ideogram(
    request,
    db,
    auth,
    team_id,
    order_by,
    search,
    page,
    page_size,
    start_date,
    end_date
  )

  return custom_response(
    jsonable_encoder(ideograms),
    StatusCode.HTTP_OK
  )


@router.get("/{id}", response_model=dict)
async def get_by_id(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Get ideogram by id.
  """
  res = await get_ideogram_by_id(id, request, db, auth)
  if not res.get('success'):
    return custom_response(
      jsonable_encoder(res),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(res),
    StatusCode.HTTP_OK
  )


@router.put("/{id}", response_model=Dict)
async def update(
  id: str,
  data: UpdateIdeogramDto,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update.
  """
  ideogram = await update_ideogram(id, data, request, db, auth)
  if not ideogram.get('success'):
    return custom_response(
      jsonable_encoder(ideogram),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(ideogram),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_ideogram(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete.
  """
  deleted = await remove_ideogram(id, request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
