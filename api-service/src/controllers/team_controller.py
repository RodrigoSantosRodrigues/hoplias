from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, paginate
from motor.motor_asyncio import AsyncIOMotorCollection

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.team_application import (
  create_team,
  get_team,
  get_by_search,
  update_team,
  remove_team,
  exit_team,
  remove_from_team
)
from ..domain.interfaces.request.team_request import CreateTeam, UpdateTeam
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("", response_model=Dict)
async def create(
  data: CreateTeam,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Create team.
  """
  user = await create_team(data, request, db, auth)
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
  order_by: str = None,
  search: str = None,
  page: int = 1,
  page_size: int = 10
) -> Any:
  """
    Get list.
  """
  teams = await get_by_search(
    request,
    db,
    auth,
    order_by,
    search,
    page,
    page_size
  )
  return custom_response(
    jsonable_encoder(jsonable_encoder(teams)),
    StatusCode.HTTP_OK
  )


@router.get("/{id}", response_model=Dict)
async def get(
  request: Request,
  id: str = None,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Get.
  """
  team = await get_team(id, request, db, auth)
  if not team.get('success'):
    return custom_response(
      jsonable_encoder(team),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(team),
    StatusCode.HTTP_OK
  )


@router.put("/{id}", response_model=Dict)
async def update(
  id: str,
  data: UpdateTeam,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update team.
  """
  team = await update_team(id, data, request, db, auth)
  if not team.get('success'):
    return custom_response(
      jsonable_encoder(team),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(team),
    StatusCode.HTTP_OK
  )


@router.put("/exit/{id}", response_model=Dict)
async def exit(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update.
  """
  team = await exit_team(id, request, db, auth)
  if not team.get('success'):
    return custom_response(
      jsonable_encoder(team),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(team),
    StatusCode.HTTP_OK
  )


@router.put("/remove-from-team/{id}/{user_id}", response_model=Dict)
async def remove_from(
  id: str,
  user_id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Update.
  """
  team = await remove_from_team(id, user_id, request, db, auth)
  if not team.get('success'):
    return custom_response(
      jsonable_encoder(team),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(team),
    StatusCode.HTTP_OK
  )


@router.delete("/{id}", response_model=Dict)
async def delete_team(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete team.
  """
  deleted = await remove_team(id, request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
