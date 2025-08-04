from typing import Any, Dict
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime, timedelta
import json

from ..helpers.authentication import Auth
from ..domain.interfaces.dto.user_dto import UserDto, UserRecoverDto
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
from ..infra.repository.user_repository import UserRepository
from ..infra.repository.user_recover_repository import UserRecoverRepository
from ..infra.repository.invitation_repository import InvitationRepository
from ..infra.repository.grant_repository import GrantRepository
from ..infra.config import token_expires_in
from ..infra.base.client_ses import ClientSes
from ..infra.base.client_zohomail import ClientZoho
from ..infra.base.client_google_auth import ClientGoogleAuth
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.enums.rules_enum import RolesEnum
from ..helpers.utils import generate_hash, verify_password, generate_code, to_boolean
from ..helpers.mappers import FileManagerMappers


async def create_token(
  data: Login,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  if not data.email or not data.password:
    return {
      'error': True,
      'message': MessagesEnum.EMPTY_FIELD_LOGIN
    }

  user_repository = UserRepository(db)
  user = await user_repository.get_by_email(
    email=data.email
  )

  if not user:
    return {
      'error': True,
      'message': MessagesEnum.LOGIN_NOT_FOUND
    }

  if not user.get('active'):
    return {
      'error': True,
      'message': MessagesEnum.LOGIN_NOT_FOUND
    }

  check = verify_password(data.password, user.get('password'))
  if not check:
    return {
      'error': True,
      'message': MessagesEnum.LOGIN_CREDENTIALS_ERROR
    }

  token = await Auth.generate_token(
    str(user.get('_id')),
    request.app.config.JWT_SIGNATURE_TOKEN
  )
  user['password'] = None

  return {
    'error': False,
    'token': token,
    'data': {**user, "id": str(user.get('_id'))},
    'expires_in': token_expires_in
  }


async def create_token_desktop(
  data: Login,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  DESKTOP_MODE_AUTH = to_boolean(request.app.config.DESKTOP_MODE_AUTH)
  if DESKTOP_MODE_AUTH:
    return {
      'error': True,
      'message': MessagesEnum.NOT_FOUND
    }

  if not data.email:
    return {
      'error': True,
      'message': MessagesEnum.EMPTY_FIELD_LOGIN
    }

  user_repository = UserRepository(db)
  user = await user_repository.get_by_email(
    email=data.email
  )

  if not user:
    data_user = CreateUser(
      email='default@mail.com',
      password=generate_hash('root'),
      active=True,
      name='Admin',
    )
    user = await user_repository.create(data_user)

  token = await Auth.generate_token(
    str(user.get('_id')),
    request.app.config.JWT_SIGNATURE_TOKEN
  )
  user['password'] = None

  return {
    'error': False,
    'token': token,
    'data': {**user, "id": str(user.get('_id'))},
    'expires_in': token_expires_in
  }


async def create_user(
  data: CreateUser,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  user_repository = UserRepository(db)
  user_recover_repository = UserRecoverRepository(db)
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)
  client_ses = ClientSes(request.app.config)
  client_zoho = ClientZoho(request.app.config)
  response_email = None

  data.setPassword(None)

  if await user_repository.get_by_email(data.email):
    return {
      'success': False,
      'message': MessagesEnum.EMAIL_ALREAD_EXISTS
    }

  code = generate_code()
  expiration_in_days = request.app.config.RECOVER_CODE_EXPIRATION_DAYS
  expiration_date = datetime.utcnow() + timedelta(days=int(expiration_in_days))

  aws_key = request.app.config.AWS_ACCESS_KEY_ID
  if aws_key:
    response_email = await client_ses.send_template_email(
      request=request,
      to_email=data.email,
      subject=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_SUBJECT,
      template_name=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_NAME,
      code=code
    )

  if not aws_key and request.app.config.MAIL_USERNAME:
    response_email = await client_zoho.send_template_email(
      to_email=data.email,
      subject=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_SUBJECT,
      template_name=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_NAME,
      code=code
    )

  if not response_email:
    return {
      'success': False,
      'message': MessagesEnum.ERROR_IN_SEND_EMAIL
    }

  data.setNotActive(False)

  user = await user_repository.create(data)

  if data.invite_id:
    invitation = await invitation_repository.get_by_id(data.invite_id)
    if not invitation.get('revoked') and not invitation.get('actived') and data.email == invitation.get('email'):
      grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
      if not grant.get('revoked') and not grant.get('actived') :
        await invitation_repository.update(invitation, {'actived': True, 'guest_user_id': user.get('_id') })
        await grant_repository.update(grant, {'actived': True, 'guest_user_id': user.get('_id') })
  
  message_id = response_email.get('message_id', None) if response_email else None

  await user_recover_repository.create(
    UserRecoverDto(
      user_id=user.get('_id'),
      old_password=user.get('password'),
      code=code,
      expiration_in_days=expiration_in_days,
      expiration_date=expiration_date,
      message_id=message_id,
      validated=False,
      created_by_user=user.get('_id'),
    )
  )

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'message_id': message_id
  }


async def create_user_google(
  data: CreateUserGoogle,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  user_repository = UserRepository(db)
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)
  client_google_auth = ClientGoogleAuth(request.app.config)

  user_info = client_google_auth.validate_google_token(data.token)
  if not user_info:
    return {
      'error': True,
      'message': MessagesEnum.LOGIN_CREDENTIALS_ERROR
    }

  email = user_info.get('email')
  user_data = await user_repository.get_by_email(email)
  if not user_data:
    user = CreateUser(
      email=user_info.get('email'),
      name=user_info.get('name'),
      picture=user_info.get('picture'),
      password=user_info.get(''),
      active=True,
      actived_at=datetime.utcnow()
    )
    await user_repository.create(user)
    user_data = await user_repository.get_by_email(email)
    
    if data.invite_id:
      invitation = await invitation_repository.get_by_id(data.invite_id)
      if not invitation.get('revoked') and not invitation.get('actived') and email == invitation.get('email'):
        grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
        if not grant.get('revoked') and not grant.get('actived') :
          await invitation_repository.update(invitation, {'actived': True})
          await grant_repository.update(grant, {'actived': True})

  token = await Auth.generate_token(
    str(user_data.get('_id')),
    request.app.config.JWT_SIGNATURE_TOKEN
  )
  user_data['password']= None

  return {
    'error': False,
    'token': token,
    'data': {**user_data, "id": str(user_data.get('_id'))},
    'expires_in': token_expires_in
  }


async def create_token_chatbot(
  data: AccessChatbot,
  request: Request,
  db: AsyncIOMotorCollection
) -> Any:
  if not data.email:
    return {
      'error': True,
      'message': MessagesEnum.EMPTY_FIELD_LOGIN
    }

  user_repository = UserRepository(db)
  user = await user_repository.get_by_email(
    email=data.email
  )

  if not user:
    data_user = CreateUser(
      email=data.email,
      chatbot_user_id=data.chatbot_user_id,
      active=True,
      name=data.name,
    )
    user = await user_repository.create(data_user)

  token = await Auth.generate_token(
    str(user.get('_id')),
    request.app.config.JWT_SIGNATURE_TOKEN
  )
  user['password'] = None

  return {
    'error': False,
    'token': token,
    'data': {**user, "id": str(user.get('_id'))},
    'expires_in': token_expires_in
  }


async def get_user(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int,
) -> Any:
  user_repository = UserRepository(db)
  user = await user_repository.get_by_id(auth)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  user['password']= None
  return {**user, "id": str(user.get('_id'))}


async def update_user(
  data: UpdateUser,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int
) -> Any:
  if data.password:
    data.setPassword(generate_hash(data.password))

  user_repository = UserRepository(db)

  user = await user_repository.get_by_id(auth)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  if data.email:
    find_user_mail = await user_repository.get_by_email(data.email)
    if find_user_mail and find_user_mail.get('_id') != auth:
      return {
        'success': False,
        'message': MessagesEnum.EMAIL_ALREAD_EXISTS
      }

  data.modified_by_user = auth
  data.team_id = user.get("team_id")
  data.active = user.get('active')
  user = await user_repository.update(user, data.dict(exclude_unset=True))
  user['password']= None

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': user
  }


async def recover_password_user(
  data: RecoverPasswordUser,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  user_repository = UserRepository(db)
  user_recover_repository = UserRecoverRepository(db)
  client_ses = ClientSes(request.app.config)
  client_zoho = ClientZoho(request.app.config)
  response_email = None

  user = await user_repository.get_by_email(data.email)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  recover_active = await user_recover_repository.get_pending_validations(user_id=user.get('_id'))
  if recover_active:
    return {
      'success': True,
      'message': MessagesEnum.ALREAD_EXISTS,
      'message_id': recover_active.get('message_id')
    }

  code = generate_code()
  expiration_in_days = request.app.config.RECOVER_CODE_EXPIRATION_DAYS
  expiration_date = datetime.utcnow() + timedelta(days=int(expiration_in_days))

  aws_key = request.app.config.AWS_ACCESS_KEY_ID
  if request.app.config.AWS_ACCESS_KEY_ID:
    response_email = await client_ses.send_template_email(
      request=request,
      to_email=user.get('email'),
      subject=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_SUBJECT,
      template_name=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_NAME,
      code=code
    )

  if not aws_key and request.app.config.MAIL_USERNAME:
    response_email = await client_zoho.send_template_email(
      to_email=user.get('email'),
      subject=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_SUBJECT,
      template_name=FileManagerMappers.TEMPLATE_EMAIL_FORGOT_NAME,
      code=code
    )

  if not response_email:
    return {
      'success': False,
      'message': MessagesEnum.ERROR_IN_SEND_EMAIL
    }

  message_id = response_email.get('message_id')

  await user_recover_repository.create(
    UserRecoverDto(
      user_id=user.get('_id'),
      old_password=user.get('password'),
      code=code,
      expiration_in_days=expiration_in_days,
      expiration_date=expiration_date,
      message_id=message_id,
      validated=False,
      created_by_user=user.get('_id'),
    )
  )

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'message_id': message_id
  }


async def validate_code_user(
  data: CodeValidationUser,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  user_repository = UserRepository(db)
  user_recover_repository = UserRecoverRepository(db)

  recover = await user_recover_repository.get_code(code=data.code)
  if not recover:
    return {
      'success': False,
      'message': MessagesEnum.TOKEN_NOT_FOUND
    }

  user = await user_repository.get_by_id(recover.get('user_id'))
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  recover['validated'] = True
  recover['modified_by_user'] = user.get('_id')
  await user_recover_repository.update(recover, recover)

  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
  }


async def update_password_user(
  data: UpdatePasswordUser,
  request: Request,
  db: AsyncIOMotorCollection,
) -> Any:
  user_repository = UserRepository(db)
  user_recover_repository = UserRecoverRepository(db)

  recover_valid = await user_recover_repository.get_valid_code(code=data.code)
  if not recover_valid:
    return {
      'success': False,
      'message': MessagesEnum.TOKEN_NOT_VALID
    }

  user = await user_repository.get_by_id(recover_valid.get('user_id'))
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  user['active'] = True
  user['password']= generate_hash(data.password)
  recover_valid['validated'] = True
  recover_valid['modified_by_user'] = user.get('_id')
  await user_repository.update(user, user)
  await user_recover_repository.update(recover_valid, recover_valid)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED_PASSWORD,
  }


async def archive_user(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict[str, str]:
  user_repository = UserRepository(db)
 
  user = await user_repository.get_by_id(auth)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await user_repository.update(user, UserDto(
    active=False,
    deleted_by_user=user.get('_id'),
    deleted_at=datetime.utcnow()
  ).dict(exclude_unset=True))

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }


async def remove_user(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict[str, str]:
  user_repository = UserRepository(db)

  user = await user_repository.get_by_id(auth)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await user_repository.delete(user)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
