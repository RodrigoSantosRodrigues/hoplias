from typing import Any, Dict
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection

from ..domain.interfaces.request.invitation_request import CreateInvitation, UpdateInvitation
from ..domain.interfaces.request.grant_request import CreateGrant
from ..domain.interfaces.request.share_request import CreateShare
from ..infra.repository.invitation_repository import InvitationRepository
from ..infra.repository.grant_repository import GrantRepository
from ..infra.repository.grant_repository import GrantRepository
from ..infra.repository.share_repository import ShareRepository
from ..infra.repository.user_repository import UserRepository
from ..infra.base.client_ses import ClientSes
from ..infra.base.client_zohomail import ClientZoho
from ..domain.enums.messages_enum import MessagesEnum
from ..helpers.mappers import FileManagerMappers


async def create_invitation(
  data: CreateInvitation,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  def get_item_id_from_dto(dto: CreateInvitation):
    fields = {
        'specie_id': dto.specie_id,
        'ideogram_id': dto.ideogram_id,
        'address_id': dto.address_id,
        'folder_id': dto.folder_id,
        'kariotype_id': dto.kariotype_id,
    }

    for field, value in fields.items():
        if value is not None:
            return value 

  invitation_repository = InvitationRepository(db)
  user_repository  = UserRepository(db)
  grant_repository = GrantRepository(db)
  share_repositry = ShareRepository(db)
  #client_ses = ClientSes(request.app.config)
  client_zoho = ClientZoho(request.app.config)

  invitation = await invitation_repository.get_invite(auth, data.team_id, data.email, get_item_id_from_dto(data))
  if invitation:
    return {
      'success': False,
      'message': MessagesEnum.ALREAD_EXISTS
    }
  
  user = await user_repository.get_by_email(data.email)

  data.owner_user_id = auth
  data.guest_user_id = user.get('_id') if user else None
  data.actived = False
  data.revoked = False
  data.send_mail = False
  invitation = await invitation_repository.create(data)

  if any([
      data.specie_id,
      data.ideogram_id,
      data.address_id,
      data.folder_id,
      data.kariotype_id
  ]):
    share = CreateShare(
      invitation_id=invitation.get('_id'),
      actived=False,
      revoked=False,
      owner_user_id=auth,
      guest_user_id=user.get('_id') if user else None,
      roles=data.roles,
      rules=data.rules,
      team_id=data.team_id,
      specie_id=data.specie_id,
      ideogram_id=data.ideogram_id,
      address_id=data.address_id,
      folder_id=data.folder_id,
      kariotype_id=data.kariotype_id
    )
    await share_repositry.create(share)
  else:
    grant = CreateGrant(
      invitation_id=invitation.get('_id'),
      actived=False,
      revoked=False,
      owner_user_id=auth,
      guest_user_id=user.get('_id') if user else None,
      roles=data.roles,
      rules=data.rules,
      team_id=data.team_id
    )
    await grant_repository.create(grant)
    
  # response_email = await client_ses.send_template_email(
  #   request=request,
  #   to_email=data.email,
  #   subject=FileManagerMappers.TEMPLATE_EMAIL_INVITE_SUBJECT,
  #   template_name=FileManagerMappers.TEMPLATE_EMAIL_INVITE_NAME,
  #   path='/user/register?invite={0}'.format(invitation.get('_id')) if not user else '/app?invite={0}'.format(invitation.get('_id'))
  # )

  response_email = await client_zoho.send_template_email(
    to_email=data.email,
    subject=FileManagerMappers.TEMPLATE_EMAIL_INVITE_SUBJECT,
    template_name=FileManagerMappers.TEMPLATE_EMAIL_INVITE_NAME,
    path='/user/register?invite={0}'.format(invitation.get('_id')) if not user else '/app?invite={0}'.format(invitation.get('_id'))
  )

  if response_email:
    invitation = await invitation_repository.get_by_id(invitation.get('_id'))
    await invitation_repository.update(invitation, { 'send_mail': True })

  return {
    'success': True,
    'message': MessagesEnum.CREATED
  }


async def get_by_search(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str,
  order_by: str,
  search: str,
  page: int = 1,
  page_size: int = 10
) -> Any:
  invitation_repository = InvitationRepository(db)

  invitates = await invitation_repository.get_by_user_or_team(
    order_by=order_by,
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
    page=page,
    page_size=page_size
  )

  return invitates


async def get_folder_by_id(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  id: str
) -> Any:
  invitation_repository = InvitationRepository(db)

  invitate = await invitation_repository.get_by_id(id)
  if not invitate:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  return {
      'success': True,
      'message': MessagesEnum.SUCCESS,
      'data': {**invitate, "id": str(invitate.get('_id'))}
    }


async def update_invitation(
  id: str,
  data: UpdateInvitation,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str = None
) -> Any:
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)

  data.modified_by_user = auth

  invitation = await invitation_repository.get_by_id(id)
  if not invitation:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }
  
  new_grant = {
    'modified_by_user': auth
  }
  new_invitation = {
    'modified_by_user': auth
  }
  if data.roles:
    new_grant['roles'] = data.roles
  if data.rules:
    new_grant['rules'] = data.rules
  
  if data.revoked:
    new_grant['revoked'] = data.revoked
    new_invitation['revoked'] = data.revoked

  grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
  await grant_repository.update(grant, new_grant)

  folder_updated = await invitation_repository.update(invitation, new_invitation)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': {**folder_updated, "id": str(folder_updated.get('_id'))}
  }


async def accept_invitation(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)
  user_repository  = UserRepository(db)

  invitation = await invitation_repository.get_by_id(id)
  if not invitation:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }
  
  user = await user_repository.get_by_id(auth)

  if not invitation.get('revoked') and not invitation.get('actived') and user.get('email') == invitation.get('email'):
    grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
    if not grant.get('revoked') and not grant.get('actived') :
      await invitation_repository.update(invitation, {'actived': True, 'guest_user_id': user.get('_id') })
      await grant_repository.update(grant, {'actived': True, 'guest_user_id': user.get('_id') })

  return {
    'success': True,
    'message': MessagesEnum.UPDATED
  }


async def remove_invitation(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str = None
) -> Dict[str, str]:
  invitation_repository = InvitationRepository(db)

  invitate = await invitation_repository.get_by_id(id)
  if not invitate:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await invitation_repository.delete(invitate)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
