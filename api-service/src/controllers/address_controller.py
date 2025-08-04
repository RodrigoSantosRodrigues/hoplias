from typing import Any, Dict
from fastapi import APIRouter, Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder
from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.address_application import (
  create_address,
  create_address_group,
  get_address_by_id,
  get_by_search,
  get_address_by_team_or_user,
  get_address_by_specie,
  update_address,
  remove_address
)
from ..domain.interfaces.request.address_request import (
  CreateAddress,
  CreateAddressGroup,
  UpdateAddress
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateAddress,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Dict:
  """
    Create address.
  """
  res = await create_address(data, request, db, auth)
  if not res.get('success'):
    return custom_response(
      jsonable_encoder(res),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(res),
    StatusCode.HTTP_OK
  )


@router.post("/group", response_model=Dict)
async def create_group(
  data: CreateAddressGroup,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create group address.
  """
  res = await create_address_group(data, request, db, auth)
  if not res.get('success'):
    return custom_response(
      jsonable_encoder(res),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(res),
    StatusCode.HTTP_OK
  )


@router.get("/search", response_model=dict)
async def get_list(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  search: str = None,
  team_id: str = None
) -> Any:
  """
    Get list by no paginate.
  """
  addresses = await get_by_search(
    search,
    request,
    db,
    auth,
    team_id
  )
  return custom_response(
    jsonable_encoder(addresses),
    StatusCode.HTTP_OK
  )


@router.get("/query", response_model=dict)
async def get_address_query(
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
    Get address, paginate.
  """
  address = await get_address_by_team_or_user(
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
    jsonable_encoder(address),
    StatusCode.HTTP_OK
  )


@router.get("/by-specie/{specie_id}", response_model=dict)
async def get_by_specie(
  specie_id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None
) -> Any:
  """
    Get address by specie_id.
  """
  res = await get_address_by_specie(request, db, auth, specie_id, team_id)

  return custom_response(
    jsonable_encoder(res),
    StatusCode.HTTP_OK
  )


@router.get("/{address_id}", response_model=dict)
async def get_by_id(
  address_id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Get address by id.
  """
  res = await get_address_by_id(address_id, request, db, auth)
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
  data: UpdateAddress,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update.
  """
  res = await update_address(id, data, request, db, auth)
  if not res.get('success'):
    return custom_response(
      jsonable_encoder(res),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(res),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_address(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete.
  """
  deleted = await remove_address(id, request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
