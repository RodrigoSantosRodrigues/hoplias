from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, paginate

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.kariotype_application import (
  create_kariotype,
  update_kariotype,
  get_by_search,
  get_kariotype_by_id,
  remove_kariotype
)
from ..domain.interfaces.request.kariotype_request import (
  CreateKariotype,
  UpdateKariotype
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateKariotype,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create kariotype.
  """
  user = await create_kariotype(data, request, db, auth)
  if not user.get('success'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )


@router.get("/search", response_model=dict)
async def get_list(
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
  status: str = None,
  by_today: bool = False
) -> Any:
  """
    Get list.
  """
  kariotypes = await get_by_search(
    request,
    db,
    auth,
    team_id,
    order_by,
    search,
    page,
    page_size,
    start_date,
    end_date,
    status,
    by_today,
  )

  return custom_response(
    jsonable_encoder(kariotypes),
    StatusCode.HTTP_OK
  )


@router.get("/{id}", response_model=dict)
async def by_id(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  page: int = 1,
  filter_type: str = None
) -> Any:
  """
    Get kariotype by id.
  """
  res = await get_kariotype_by_id(id, request, db, auth, page, filter_type)
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
  data: UpdateKariotype,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update user.
  """
  user = await update_kariotype(id, data, request, db, auth)
  if not user.get('success'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_kariotype(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete.
  """
  deleted = await remove_kariotype(id, request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
