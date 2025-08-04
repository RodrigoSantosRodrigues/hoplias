from typing import Any, Dict
from fastapi import APIRouter, Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.folder_application import (
  create_folder,
  update_folder,
  get_by_search,
  get_folder_by_id,
  remove_folder
)
from ..domain.interfaces.request.folder_request import (
  CreateFolderDto,
  UpdateFolderDto
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateFolderDto,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create folder.
  """
  folder = await create_folder(data, request, db, auth)
  if not folder.get('success'):
    return custom_response(
      jsonable_encoder(folder),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(folder),
    StatusCode.HTTP_OK
  )


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
async def query_by_id(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Get folder.
  """
  folder = await get_folder_by_id(request, db, auth, id)
  if not folder.get('success'):
    return custom_response(
      jsonable_encoder(folder),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(folder),
    StatusCode.HTTP_OK
  )


@router.put("/{id}", response_model=Dict)
async def update(
  id: str,
  data: UpdateFolderDto,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
) -> Any:
  """
    Update folder.
  """
  folder = await update_folder(id, data, request, db, auth, team_id)
  if not folder.get('success'):
    return custom_response(
      jsonable_encoder(folder),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(folder),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_volunteer(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
) -> Any:
  """
    Delete.
  """
  deleted = await remove_folder(id, request, db, auth, team_id)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
