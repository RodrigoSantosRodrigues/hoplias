# -*- coding: utf-8 -*-
#/src/controllers/AccountService.py
"""
  ------------------------------------------------------------------------
                      Service Segmentation
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
    #convert string data to numpy array
    numpyImage = numpy.fromstring(req_data, numpy.uint8)
    # convert numpy array to image
    image = cv2.imdecode(numpyImage, cv2.IMREAD_COLOR)
    
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

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
