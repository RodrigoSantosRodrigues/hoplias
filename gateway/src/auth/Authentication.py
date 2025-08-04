# -*- coding: utf-8 -*-
#src/auth/Authentication
"""
    ------------------------------------------------------------------------
                        Auth
    ------------------------------------------------------------------------
"""
import jwt
import os
import datetime
from flask import json, Response, request, g
from functools import wraps

class Auth():
  """
  Auth Class
  """
  @staticmethod
  def decode_token(token):
    """
    Decode token method

    """
    re = {'data': {}, 'error': {}}
    try:
      
      payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
      re['data'] = {'user_id': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re
    
  @staticmethod
  def validate_token(token):
    """
    Decode token method

    """
    re = {'data': {}, 'error': {}}
    try:
      if token == 'htj_5y2LF4Q8z\tyusdfdfd/4589':
        re['data'] = {'user_id': 'api-service'}
      else:
        re['error'] = {'message': 'token invalid, please!'}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re

  # decorator
  @staticmethod
  def auth_required(func):
    """
    Auth decorator
    
    """
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'Authentication token is not available, please request to get one'}),
          status=403
        )
      token = request.headers.get('api-token')
      data = Auth.validate_token(token)
      if data['error']:
        return Response(
          mimetype="application/json",
          response=json.dumps(data['error']),
          status=403
        )
        
      g.user = {'id': data['data']['user_id']}
      return func(*args, **kwargs)
    return decorated_auth
