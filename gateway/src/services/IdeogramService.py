# -*- coding: utf-8 -*-
#/src/controllers/ClassificationService.py
"""
  ------------------------------------------------------------------------
                      Service Classification
  ------------------------------------------------------------------------
"""
import numpy
import cv2
import json
import logging

from ..config import rabbit_config
from flask import request, g, Blueprint, json, Response
from ..auth.Authentication import Auth
from ..helpers.CallRpc import rpc_proxy

ideogram_api = Blueprint('ideogram_api', __name__)

@ideogram_api.route('/ideogram', methods=['POST'])
@Auth.auth_required
def ideogram():
  try:
    req_data = request.get_json()
    response = rpc_proxy('ideogram', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
