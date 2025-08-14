# -*- coding: utf-8 -*-
#/src/controllers/ClassificationService.py
"""
"""
import numpy
import cv2
import json
import logging
from flask import request, g, Blueprint, json, Response
import numpy as np

from ..auth.Authentication import Auth
from ..helpers.CallRpc import rpc_proxy
from ..helpers.ProducerQueue import producer_queue

classification_api = Blueprint('classification_api', __name__)

@classification_api.route('/enqueue-centromere', methods=['POST'])
@Auth.auth_required
def producer_centromere():
  try:
    req_data = request.get_json()
    response = producer_queue('centromere_queue', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response producer: {error}")
    return custom_response({'error': str(error)}, 500)

@classification_api.route('/centromere', methods=['POST'])
@Auth.auth_required
def centromere():
  try:
    req_data = request.get_json()
    response = rpc_proxy('centromere', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)

@classification_api.route('/enqueue-preclassification', methods=['POST'])
@Auth.auth_required
def producer_preclassification():
  try:
    req_data = request.get_json()
    response = producer_queue('preclassification_queue', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response producer: {error}")
    return custom_response({'error': str(error)}, 500)

@classification_api.route('/preclassification', methods=['POST'])
@Auth.auth_required
def preclassification():
  try:
    req_data = request.get_json()
    response = rpc_proxy('preclassification', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)

@classification_api.route('/classification', methods=['POST'])
@Auth.auth_required
def classification():
  try:
    req_data = request.get_json()
    response = rpc_proxy('classification', req_data)
    return custom_response(response, response.get('status_code'))
  except Exception as error:
    logging.error(f"Response rpc: {error}")
    return custom_response({'error': error}, 500)

def custom_response(res, status_code=200):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
