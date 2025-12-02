import jwt
import datetime
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer

from .mappers import StatusCode, GenericMessages, RoutePathChatbotToken
from ..infra.config import token_expires_in, logger
from ..infra.repository.user_repository import UserRepository
from ..infra.repository.team_repository import TeamRepository
#from ..helpers.control_access import ControlAccess

security = HTTPBearer()


class Auth:

  @staticmethod
  async def generate_token(user_id, jwt_signature):
    """
    Generate Token Method
    """
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=int(token_expires_in)),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
      }
      return jwt.encode(
        payload,
        jwt_signature,
        'HS256'
      )
    except Exception as e:
      raise HTTPException(
            status_code=StatusCode.HTTP_NOT_CREATE_TOKEN,
            detail='{0}:{1}'.format(GenericMessages.ERROR_GENERATE_TOKEN, str(e)),
            headers={"WWW-Authenticate": "Basic"},
        )


  @staticmethod
  def decode_token(token, jwt_signature):
    """
    Decode token method
    """
    re = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, jwt_signature, algorithms=['HS256'])
      re['data'] = {'user_id': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as ex:
      re['error'] = {'message': '{0}:{1}'.format(GenericMessages.EXPIRED_TOKEN, str(ex))}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': GenericMessages.INVALID_TOKEN}
      return re

  async def auth_required(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security)
  ):
    """
    Auth decorator
    """
    try:

      #control_access = ControlAccess(request.url.path, request.method)
      user_repository = UserRepository(request.state.db)
      team_repository = TeamRepository(request.state.db)

      token = credentials.credentials
      api_token_chatbot = request.headers.get("api-token-key")

      if request.url.path == RoutePathChatbotToken:
        if api_token_chatbot != request.app.config.CHATBOT_SECRET_KEY:
          logger.error(f"An error occurred authentication chatbot: {api_token_chatbot}", exc_info=True)
          raise HTTPException(
            status_code=StatusCode.HTTP_ERROR_TOKEN,
            detail=GenericMessages.INVALID_TOKEN,
            headers={"WWW-Authenticate": "Basic"},
          )
        return True

      if not token:
        raise HTTPException(
            status_code=StatusCode.HTTP_NOT_TOKEN,
            detail={'error': GenericMessages.NOT_TOKEN},
            headers={"WWW-Authenticate": "Basic"},
        )

      data = Auth.decode_token(token, request.app.config.JWT_SIGNATURE_TOKEN)
      if data['error']:
        raise HTTPException(
            status_code=StatusCode.HTTP_ERROR_TOKEN,
            detail=data['error'],
            headers={"WWW-Authenticate": "Basic"},
        )

      user_id = data['data']['user_id']
      user = await user_repository.get_by_id(user_id)
      if not user:
        raise HTTPException(
            status_code=StatusCode.HTTP_INVALID_USER,
            detail={'message': GenericMessages.USER_NOT_FOUND},
            headers={"WWW-Authenticate": "Basic"},
        )

      # team = await team_repository.get_by_id(user.team_id)
      # if not team:
      #   raise HTTPException(
      #       status_code=StatusCode.HTTP_INVALID_USER,
      #       detail={'message': GenericMessages.USER_NOT_FOUND},
      #       headers={"WWW-Authenticate": "Basic"},
      #   )

      # access = control_access.get_access()
      # required_roles = access.get('roles', [])
      # required_rules = access.get('rules', [])

      # if required_roles:
      #   user_has_role = any(role in user.roles for role in access.get('roles', []))
      #   if not user_has_role:
      #     raise HTTPException(
      #       status_code=StatusCode.HTTP_NOT_ROLE,
      #       detail={'message': GenericMessages.ROLE_NOT_FOUND},
      #       headers={"WWW-Authenticate": "Basic"},
      #     )

      # if required_rules:
      #   user_has_rule = any(rule in user.rules for rule in access.get('rules', []))
      #   if not user_has_rule:
      #     raise HTTPException(
      #       status_code=StatusCode.HTTP_NOT_ROLE,
      #       detail={'message': GenericMessages.RULE_NOT_FOUND},
      #       headers={"WWW-Authenticate": "Basic"},
      #     )

      return user.get('_id')
    except Exception as e:
      logger.error(f"An error occurred authentication: {e}", exc_info=True)
      if isinstance(e, HTTPException):
        raise HTTPException(
          status_code=e.status_code,
          detail={'error': '{0}{1}'.format(GenericMessages.EXCEPTION, str(e.detail.get('message')))},
          headers={"WWW-Authenticate": "Basic"},
        )
      raise HTTPException(
          status_code=StatusCode.HTTP_INTERNAL_SERVER_ERROR,
          detail={'error': '{0}{1}'.format(GenericMessages.EXCEPTION, str(e))},
          headers={"WWW-Authenticate": "Basic"},
        )

  async def auth_required_chatbot(
    request: Request
  ):
    """
    Auth decorator chatbot auth
    """
    try:
      api_token_chatbot = request.headers.get("api-token-key")
      logger.error(f"chatbot key: {api_token_chatbot}")
 
      if api_token_chatbot != request.app.config.CHATBOT_SECRET_KEY:
        logger.error(f"Entrou: {api_token_chatbot}")
        raise HTTPException(
          status_code=StatusCode.HTTP_ERROR_TOKEN,
          detail=GenericMessages.INVALID_TOKEN,
          headers={"WWW-Authenticate": "Basic"},
        )
      return True
    except Exception as e:
      logger.error(f"An error occurred authentication: {e}")
      if isinstance(e, HTTPException):
        raise HTTPException(
          status_code=e.status_code,
          detail={'error': '{0}{1}'.format(GenericMessages.EXCEPTION, str(e.detail.get('message')))},
          headers={"WWW-Authenticate": "Basic"},
        )
      raise HTTPException(
          status_code=StatusCode.HTTP_INTERNAL_SERVER_ERROR,
          detail={'error': '{0}{1}'.format(GenericMessages.EXCEPTION, str(e))},
          headers={"WWW-Authenticate": "Basic"},
        )
