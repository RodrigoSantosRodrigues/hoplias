from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, paginate

from ..helpers.utils import custom_response, get_db
from ..helpers.mappers import  StatusCode
from ..application.user_application import (
  create_token,
  create_token_desktop,
  create_token_chatbot,
  create_user,
  create_user_google,
  update_user,
  get_user,
  recover_password_user,
  validate_code_user,
  update_password_user,
  archive_user,
  remove_user
)
from ..domain.interfaces.request.user_request import (
  Login,
  AccessChatbot,
  CreateUser,
  UpdateUser,
  RecoverPasswordUser,
  CodeValidationUser,
  UpdatePasswordUser,
  CreateUserGoogle
)
from ..helpers.authentication import Auth

router = APIRouter()


@router.post("/auth", response_model=Dict)
async def auth(
  data: Login,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Get token of login credentials.
  """
  data = await create_token(data, request, db)
  if data.get('error'):
    return custom_response(
      jsonable_encoder(data),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(data),
    StatusCode.HTTP_OK
  )

@router.post("", response_model=Dict)
async def create(
  data: CreateUser,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Create user.
  """
  user = await create_user(data, request, db)
  if not user.get('success'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )
  
  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )


@router.post("/auth-desktop", response_model=Dict)
async def auth_desktop(
  data: Login,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Get token of login credentials Desktop mode.
  """
  data = await create_token_desktop(data, request, db)
  if data.get('error'):
    return custom_response(
      jsonable_encoder(data),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(data),
    StatusCode.HTTP_OK
  )

@router.post("/auth-google", response_model=Dict)
async def create_auth(
  data: CreateUserGoogle,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Create user by google.
  """
  user = await create_user_google(data, request, db)
  if user.get('error'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )
  
  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )

@router.post("/auth-chatbot", response_model=Dict)
async def auth_chatbot(
  data: AccessChatbot,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  authorized=Depends(Auth.auth_required_chatbot)
) -> Any:
  """
    Get token of login credentials chatbot mode.
  """
  data = await create_token_chatbot(data, request, db)
  if data.get('error'):
    return custom_response(
      jsonable_encoder(data),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(data),
    StatusCode.HTTP_OK
  )


@router.put("/me", response_model=Dict)
async def update(
  id: str,
  data: UpdateUser,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Update user.
  """
  user = await update_user(data, request, db, auth)
  if not user.get('success'):
    return custom_response(
      jsonable_encoder(user),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(user),
    StatusCode.HTTP_OK
  )


@router.get("/me", response_model=Dict)
async def get_me(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required),
) -> Any:
  """
    Get users.
  """
  users = await get_user(request, db, auth)

  return custom_response(
    jsonable_encoder(users),
    StatusCode.HTTP_OK
  )


@router.post("/recover-password", response_model=Dict)
async def recover_password(
  data: RecoverPasswordUser,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Recover user.
  """
  recover = await recover_password_user(data, request, db)
  if not recover.get('success'):
    return custom_response(
      jsonable_encoder(recover),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(recover),
    StatusCode.HTTP_OK
  )


@router.post("/validate-code", response_model=Dict)
async def validate_code(
  data: CodeValidationUser,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Validate user.
  """
  validate = await validate_code_user(data, request, db)
  if not validate.get('success'):
    return custom_response(
      jsonable_encoder(validate),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(validate),
    StatusCode.HTTP_OK
  )

@router.post("/update-password", response_model=Dict)
async def update_password(
  data: UpdatePasswordUser,
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
) -> Any:
  """
    Update password.
  """
  updated = await update_password_user(data, request, db)
  if not updated.get('success'):
    return custom_response(
      jsonable_encoder(updated),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(updated),
    StatusCode.HTTP_OK
  )

@router.put("/archive-user/me", response_model=Dict)
async def archive(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Archive user.
  """
  archived = await archive_user(request, db, auth)
  if not archived.get('success'):
    return custom_response(
      jsonable_encoder(archived),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(archived),
    StatusCode.HTTP_OK
  )

@router.delete("/me", response_model=Dict)
async def delete_user(
  request: Request,
  db: AsyncIOMotorCollection = Depends(get_db),
  auth=Depends(Auth.auth_required)
) -> Any:
  """
    Delete user.
  """
  deleted = await remove_user(request, db, auth)
  if not deleted.get('success'):
    return custom_response(
      jsonable_encoder(deleted),
      StatusCode.HTTP_ERROR
    )

  return custom_response(
    jsonable_encoder(deleted),
    StatusCode.HTTP_OK
  )
