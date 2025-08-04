from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, paginate

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.specie_application import (
  create_specie,
  get_by_search,
  update_specie, get_specie,
  remove_specie
)
from ..domain.interfaces.request.specie_request import (
    CreateSpecie,
    UpdateSpecie
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateSpecie,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create specie.
  """
  user = await create_specie(data, request, db, auth)
  if not user.get('success'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )


@router.get("/search", response_model=Page[Dict])
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
  folders = await get_by_search(
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
    jsonable_encoder(jsonable_encoder(folders)),
    StatusCode.HTTP_OK
  )


@router.get("/{id}", response_model=Dict)
async def get_by_id(
  request: Request,
  search: str = None,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  id: str = None
) -> Any:
  """
    Get specie.
  """
  specie = await get_specie(id, request, db, auth)
  if not specie.get('success'):
    return custom_response(
      jsonable_encoder(specie),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(specie),
    StatusCode.HTTP_OK
  )


@router.put("/{id}", response_model=Dict)
async def update(
  id: str,
  data: UpdateSpecie,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update specie.
  """
  user = await update_specie(id, data, request, db, auth)
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
async def delete_specie(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete.
  """
  deleted = await remove_specie(id, request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
