from fastapi import APIRouter

from .controllers import (
    user_controller,
    specie_controller,
    kariotype_controller,
    address_controller,
    team_controller,
    ideogram_controller,
    folder_controller,
    invitation_controller,
    notification_controller,
    proxygtw_controller,
    proxyai_controller
)

api_router = APIRouter()

api_router.include_router(
  user_controller.router,
  prefix="/user",
  tags=["User"]
)

# api_router.include_router(
#   specie_controller.router,
#   prefix="/specie",
#   tags=["Specie"]
# )

api_router.include_router(
  kariotype_controller.router,
  prefix="/kariotype",
  tags=["Kariotype"]
)

# api_router.include_router(
#   address_controller.router,
#   prefix="/address",
#   tags=["Address"]
# )

# api_router.include_router(
#   team_controller.router,
#   prefix="/team",
#   tags=["Team"]
# )

api_router.include_router(
  ideogram_controller.router,
  prefix="/ideogram",
  tags=["Ideogram"]
)

# api_router.include_router(
#   folder_controller.router,
#   prefix="/folder",
#   tags=["Folder"]
# )

api_router.include_router(
  invitation_controller.router,
  prefix="/invitation",
  tags=["Invitation"]
)

api_router.include_router(
  notification_controller.router,
  prefix="/notification",
  tags=["Notification"]
)

api_router.include_router(
  proxygtw_controller.router,
  prefix="/analyze-chromosome",
  tags=["Process CNN ML"]
)

# api_router.include_router(
#   proxyai_controller.router,
#   prefix="/tools-ai",
#   tags=["Use tools AI"]
# )
