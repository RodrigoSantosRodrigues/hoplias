# -*- coding: utf-8 -*-
"""
"""
import numpy
import json
import logging
from io import BytesIO
from imageio import imread

from ..config import rabbit_config
from flask import request, g, Blueprint, Response
from ..auth.Authentication import Auth
from ..helpers.CallRpc import rpc_proxy

segmentation_api = Blueprint('segmentation_api', __name__)

class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, numpy.ndarray):
        return obj.tolist()
    return json.JSONEncoder.default(self, obj)

@segmentation_api.route('', methods=['POST'])
@Auth.auth_required
def segmentation_create():
  try:
    req_data = request.files['image'].read()
    # convert binary data to image using imageio
    image = imread(BytesIO(req_data))
    
    data= json.dumps({'image': image, }, cls=NumpyEncoder)

    response = rpc_proxy('segmentation_create', data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)

@segmentation_api.route('/json', methods=['POST'])
@Auth.auth_required
def segmentation_create_hoplias():
  try:
    req_data = request.get_json()
    response = rpc_proxy('segmentation_create_hoplias', req_data)
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

@segmentation_api.route('/convert-image', methods=['POST'])
@Auth.auth_required
def convert_to_jpg_hoplias():
  try:
    req_data = request.get_json()
    response = rpc_proxy('convert_to_jpg_hoplias', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)
