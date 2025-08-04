import re
import base64
import secrets
import logging
import uuid
from math import ceil
from fastapi import  Request
from fastapi.responses import JSONResponse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from ..infra.base.db import PwdContext
from ..domain.enums.status_enum import StatusChromosomeEnum


def custom_response(res, status_code):
  return JSONResponse(status_code=status_code, content=res)

# [DEPENDECY]
def get_db(request: Request):
  return request.state.db

def generate_hash(password: str):
  return PwdContext.hash(password)

def verify_password(password: str, hashed_password: str):
  return PwdContext.verify(password, hashed_password)

def convertBase64String(value: str):
  return base64.b64encode(value)

def get_resource_url_s3(bucket, file_name):
  return 'https://{0}.s3.amazonaws.com/{1}'.format(bucket, file_name)

def clearDocument(value):
  dots =  value.replace('.','').replace('.','').replace('.','').replace('.','').replace('.','').replace('.','')
  spaces = dots.replace('-','').replace('-','').replace('-','').replace('-','').replace('-','').replace('-','')
  return spaces.replace(' ','').replace(' ','').replace(' ','').replace(' ','').replace(' ','').replace(' ','')

def slugify(text):
  text = re.sub(r'[^\w\s-]', '', text).strip().lower()
  text = re.sub(r'[-\s]+', '-', text)
  return text

def generate_code(length=6):
  return ''.join(secrets.choice('0123456789') for _ in range(length))

def to_boolean(value):
  if isinstance(value, bool):
      return value
  if isinstance(value, str):
      return value.lower() in ['true', '1', 'yes', 'y', 'sim', 'VERDADEIRO']
  if isinstance(value, (int, float)):
      return value == 1
  return False

def clean_base64(image_data):
  if image_data.startswith("data:image"):
    image_data = image_data.split(",")[1]

  image_data = re.sub(r'[^A-Za-z0-9+/=]', '', image_data)

  if isinstance(image_data, str):
    image_data = image_data.encode('utf-8')
  
  missing_padding = len(image_data) % 4
  if missing_padding:
    image_data += b'=' * (4 - missing_padding)
      
  return base64.b64decode(image_data)

def get_payload_remine_queue(data, contour):
  remining = []
  for idx, obj in enumerate(data, start=7):
    remining.append(
      {
        'id': idx,
        'dimension': {
          'x': None,
          'y': None
        },
        'centromere': {
          'x': None,
          'y': None
        },
        'contour': contour,
        'base64_rgb': None,
        'base64_gray': None,
        'base64_binary': None
      }
    )

  return remining

def get_payload_segmented_initial_request(data):
  polygons = list(filter(lambda obj: obj.get("type") == "polygon", data))
 
  chromosomes = []
  for obj in polygons:
    chromosomes.append({
      "left_contour": obj.get("left"),
      "top_contour": obj.get("top"),
      "contour": obj.get("points"),
      "id_chromosome":  obj.get("id"),
      "name": obj.get("name")
    })

  return chromosomes

def get_payload_after_first_centromere_request(data):
  BATCH_SIZE = 6
  current_batch = 1

  polygons = list(filter(lambda obj: obj.get("type") == "polygon", data))
  
  total_batches = ceil(len(polygons) / BATCH_SIZE)

  chromosomes = []
  for idx, obj in enumerate(polygons, start=1):
    status_centromere = StatusChromosomeEnum.PENDING
    id = str(uuid.uuid4())
 
    current_batch = ceil(idx / BATCH_SIZE)

    if current_batch == 1:
        status_centromere = StatusChromosomeEnum.PROCESSED
    elif current_batch == 2:
        status_centromere = StatusChromosomeEnum.IN_QUEUE
    else:
        status_centromere = StatusChromosomeEnum.PENDING

    manual = False
    if obj.get('name') == 'New polygon':
      manual = True
    elif obj.get('manual') == True:
      manual = True

    chromosomes.append({
      "id": id,
      "class_name": None,
      "upper_chromatide_size": None,
      "lower_chromatide_size": None,
      "checked": False,
      "size": None,
      "file_s3": None,
      "obj_area": None,
      "dimension": None,
      "left_contour": obj.get("left"),
      "top_contour": obj.get("top"),
      "contour": obj.get("points"),
      "agent_who_identified_chromosome": True if obj.get('name') == 'New polygon' else False,
      "agent_who_identified_centromere": None,
      "agent_who_identified_rotation": None,
      "centromere_coord": [None, None],
      "id_chromosome": idx,
      "left": None,
      "top": None,
      "name": f"Chromosome {idx}",
      "canva": None,
      "status_centromere":  status_centromere,
      'status_preclassification': StatusChromosomeEnum.PENDING,
      "batch_number": current_batch,
    })

    if manual:
      chromosomes[idx -1]['manual'] = manual

  return chromosomes, total_batches
