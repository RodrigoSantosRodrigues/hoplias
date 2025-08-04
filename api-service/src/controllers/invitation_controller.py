from typing import Any, Dict
from fastapi import APIRouter, Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, paginate
from motor.motor_asyncio import AsyncIOMotorCollection

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.invitation_application import (
  create_invitation,
  update_invitation,
  accept_invitation,
  get_by_search,
  get_folder_by_id,
  remove_invitation
)
from ..domain.interfaces.request.invitation_request import CreateInvitation, UpdateInvitation
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateInvitation,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create invitation.
  """
  invitate = await create_invitation(data, request, db, auth)
  if not invitate.get('success'):
    return custom_response(
      jsonable_encoder(invitate),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(invitate),
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
  page_size: int = 10
) -> Any:
  """
    Get list.
  """
  invitates = await get_by_search(
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
    jsonable_encoder(invitates),
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
    Get .
  """
  invitate = await get_folder_by_id(request, db, auth, id)
  if not invitate.get('success'):
    return custom_response(
      jsonable_encoder(invitate),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(invitate),
    StatusCode.HTTP_OK
  )


@router.put("/{id}", response_model=Dict)
async def update(
  id: str,
  data: UpdateInvitation,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
) -> Any:
  """
    Update.
  """
  invitate = await update_invitation(id, data, request, db, auth, team_id)
  if not invitate.get('success'):
    return custom_response(
      jsonable_encoder(invitate),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(invitate),
    StatusCode.HTTP_OK
  )


@router.put("/accept-invitation/{id}", response_model=Dict)
async def update(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update.
  """
  invitate = await accept_invitation(id, request, db, auth)
  if not invitate.get('success'):
    return custom_response(
      jsonable_encoder(invitate),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(invitate),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_invitation(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
  team_id: str = None,
) -> Any:
  """
    Delete.
  """
  deleted = await remove_invitation(id, request, db, auth, team_id)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
