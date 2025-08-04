from typing import Any, Dict
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection

from ..domain.interfaces.request.team_request import CreateTeam, UpdateTeam
from ..infra.repository.invitation_repository import InvitationRepository
from ..infra.repository.grant_repository import GrantRepository
from ..infra.repository.team_repository import TeamRepository
from ..infra.repository.user_repository import UserRepository
from ..domain.enums.messages_enum import MessagesEnum


async def create_team(
  data: CreateTeam,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  team_repository = TeamRepository(db)

  team = await team_repository.get_by_name(
    name=data.name,
    user_id=auth
  )
  if team:
    return {
      'success': False,
      'message': MessagesEnum.ALREAD_EXISTS
    }

  data.user_id = auth
  data.active = True
  data.created_by_user = auth
  team = await team_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': {**team, "id": str(team.get('_id'))}
  }


async def get_team(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  team_repository = TeamRepository(db)

  team = await team_repository.get_by_id(id)
  if not team:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
    'data': {**team, "id": str(team.get('_id'))}
  }


async def get_by_search(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  order_by: str,
  search: str,
  page: int = 1,
  page_size: int = 10
) -> Any:
  team_repository = TeamRepository(db)

  teams = await team_repository.get_by_user(
    order_by=order_by,
    search=search,
    user_id=auth,
    page=page,
    page_size=page_size
  )

  return teams


async def update_team(
  id: str,
  data: UpdateTeam,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  team_repository = TeamRepository(db)

  team = await team_repository.get_by_id(id)
  if not team:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  data.modified_by_user = auth
  data.user_id = team.get('user_id')
  data.team_id = team.get('team_id')

  update_data = data.dict(exclude_unset=True)

  team_updated = await team_repository.update(team, update_data)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': {**team_updated, "id": str(team_updated.get('_id'))}
  }


async def exit_team(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)
  user_repository  = UserRepository(db)

  invitation = await invitation_repository.get_by_guest_user_id(auth, id)
  if not invitation:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }
  
  user = await user_repository.get_by_id(auth)

  if user.get('email') == invitation.get('email'):
    grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
    if not grant.get('revoked'):
      await invitation_repository.update(invitation, { 'revoked': True })
      await grant_repository.update(grant, { 'revoked': True })

  return {
    'success': True,
    'message': MessagesEnum.UPDATED
  }


async def remove_from_team(
  id: str,
  user_id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  invitation_repository = InvitationRepository(db)
  grant_repository = GrantRepository(db)

  invitation = await invitation_repository.get_by_guest_user_id(user_id, id)
  if not invitation or invitation.get('owner_user_id') != auth:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  grant = await grant_repository.get_by_invitation_id(invitation.get('_id'))
  if not grant.get('revoked'):
    await invitation_repository.update(invitation, { 'revoked': True })
    await grant_repository.update(grant, { 'revoked': True })

  return {
    'success': True,
    'message': MessagesEnum.UPDATED
  }


async def remove_team(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict[str, str]:
  team_repository = TeamRepository(db)

  team = await team_repository.get_by_id(id)
  if not team:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await team_repository.delete(team)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
