from typing import Any
from fastapi import Request, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Any, Dict

from ..domain.interfaces.request.folder_request import CreateFolderDto, UpdateFolderDto
from ..infra.repository.folder_repository import FolderRepository
from ..infra.repository.invitation_repository import InvitationRepository
from ..infra.repository.category_repository import CategoryRepository
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.interfaces.dto.category_dto import CategoryData
from ..helpers.utils import slugify


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
  folder_repository = FolderRepository(db)
  invitation_repository = InvitationRepository(db)
  data = {
    'invitations': []
  }

  invitations = await invitation_repository.get_by_user_or_team(
    order_by=order_by,
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
    page=page,
    page_size=page_size
  )
  
  data['invitations'] = invitations

  return data
