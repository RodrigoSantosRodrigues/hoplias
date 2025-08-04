import re
import uuid
import numpy as np
import json
import cv2
import base64
from itertools import islice

from ..helpers.Filter import Filter
from ..helpers.Mask import Mask
from ..helpers.Extract import Extract
from ..helpers.Resize import Resize
from ..helpers.Rotation import Rotation
from ..helpers.NumpyToPng import NumpyToPng
from ..helpers.ZhangSue import ZhangSue
from ..enums.StatusEnum import StatusKariotypeEnum, StatusChromosomeEnum
from ..enums.S3Enum import Bucket
from ..services.ClientS3 import ClientS3
from ..services.ClientGoogleDrive import ClientGoogleDrive
from ..services.ClientGoogleCloud import ClientGoogleCloud
from ..services.ClientLocalSorage import ClientLocalStorage
from ..db.KariotypeCrud import KariotypeRepository


class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    return json.JSONEncoder.default(self, obj)

class ConsumerCentromereControllerv2Beta:
  def __init__(self, db, publish, logger):
    self.db = db
    self.logger = logger
    self.image_base64 = ""
    self.publish = publish
    self.image = None
    self.contour = ""
    self.masking = None
    self.filtering = None
    self.coord_sum= []
    self.properties = {}
    self.remining = []
    self.client_s3 = ClientS3()
    self.client_google_drive = ClientGoogleDrive()
    self.client_google_cloud = ClientGoogleCloud()
    self.client_local_storage = ClientLocalStorage()
    self.kariotype_repository = KariotypeRepository(self.db)

  def process_chrom(self, payload):
    id = payload.get('kariotype_id')
    self.data = payload

    self.properties = self.kariotype_repository.get_by_id(id)

    if self.properties.get('status') == StatusKariotypeEnum.CENTROMERE_LOCALIZED or \
      self.properties.get('status') == StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES:
      
      account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')

      if self.properties.get('file_s3', None) is not None:
        base_64 = self.client_s3.load_image(
          f"{account_id}/{self.properties.get('folder_s3')}/{self.properties.get('file_s3')}",
          Bucket.BUCKET
        )

      if self.properties.get('file_gcs', None) is not None:
        base_64 = self.client_google_cloud.load_image(
          f"{account_id}/{self.properties.get('folder_gcs')}/{self.properties.get('file_gcs')}",
        )

      if self.properties.get('file_local', None) is not None:
        base_64 = self.client_local_storage.load_image(
          f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}/{self.properties.get('file_local')}",
        )

      self._load_image(base_64)

      self.filtering = Filter(self.image)
      self.masking = Mask(self.filtering.morphological_filtration())

      while True:
        self.remining = [
          obj for obj in self.properties.get('chromosomes')
          if obj.get('status_centromere') in [StatusChromosomeEnum.PENDING, StatusChromosomeEnum.IN_QUEUE] and \
          obj.get('empty') is not True
        ]

        if not self.remining:
          break

        batch = list(islice(self.remining, 6))

        for chrom in batch:
          self.kariotype_repository.bulk_update(self.properties.get('_id'), [
            {
              'id_chromosome': chrom.get('id_chromosome'),
              'status_centromere': StatusChromosomeEnum.PROCESSING
            }
          ])
        
        self.centromere()
        self.properties = self.kariotype_repository.get_by_id(self.properties.get('_id'))

  def _load_image(self, base_64):
    self.image_base64 = base_64
    image_b64 = self.image_base64.split(",")[1]
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    self.image = image

  def _load_contour(self, objects) -> list:
    def format_object(item):
      return [item['x'], item['y']]

    def format_new_object(item):
      return [item['x'] - self.coord_sum[0], item['y'] - self.coord_sum[1]]

    def format_list(item):
      if len(item.get('contour')) > 0:
        if item.get('name') == "New polygon" or item.get('manual') == True:
          return list(map(format_new_object, item.get('contour')))
        else:
          return list(map(format_object, item.get('contour')))

    def format_coord(item):
      left=0
      top=0
 
      left= item.get('left')
      # if left < 0:
      #   left= left * -1
      top= item.get('top')
      # if top < 0:
      #   top= top * -1
      return [left, top]

    coord= format_coord(self.properties)
    self.coord_sum= coord
    contour = list(map(format_list, objects))
    return contour

  def _clean_base64(self, image_data):
    if image_data.startswith("data:image"):
      image_data = image_data.split(",")[1]

    image_data = re.sub(r'[^A-Za-z0-9+/=]', '', image_data)

    if isinstance(image_data, str):
      image_data = image_data.encode('utf-8')
    
    missing_padding = len(image_data) % 4
    if missing_padding:
      image_data += b'=' * (4 - missing_padding)
        
    return base64.b64decode(image_data)

  def centromere(self):
    for item in self.remining:
      contour = self._load_contour([item])
      image_mask = self.masking.build_mask(contour[0])
      extracting = Extract(self.image, image_mask, self.filtering.morphological_filtration())
      singles, masks = extracting.extract_rgb()

      resizing = Resize()
      objects_rgb = resizing.Resize_images(singles)
      objects_binaries = resizing.Resize_images(masks)

      rotating_rgb = Rotation(objects_rgb[0], objects_binaries[0], self.logger)
      rotated_image_rgb, rotated_image_rgb_binary = rotating_rgb.rotation_particle()

      rotating_gray = Rotation(objects_rgb[0], objects_binaries[0], self.logger)
      rotated_image_gray, rotated_image_gray_binary = rotating_gray.rotation_particle_gray()

      zhang_sue = ZhangSue(rotated_image_rgb, rotated_image_rgb_binary.copy(), 0)
      points = zhang_sue.skel_chromosome()

      if zhang_sue.skel is None and points is None:
        self.kariotype_repository.bulk_update(
        self.properties.get('_id'), 
        [
          { 
            'id_chromosome': item.get('id_chromosome'), 
            'empty': True,
            'status_centromere': StatusChromosomeEnum.PROCESSED
          }
        ]
      )

      converting_rgb = NumpyToPng(rotated_image_rgb, self.logger)
      image_base64_rgb = converting_rgb.convert()

      converting_gray = NumpyToPng(rotated_image_gray, self.logger)
      image_base64_gray = converting_gray.convert_gray_image(rotated_image_rgb)

      account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')
      file_rgb_name = f"{str(uuid.uuid4())}.png"
      file_gray_name = f"{str(uuid.uuid4())}.png"

      if self.properties.get('file_s3') is not None:
        self.client_s3.upload_image(
            self._clean_base64(image_base64_rgb),
            Bucket.BUCKET,
            f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
        )
        self.client_s3.upload_image(
            self._clean_base64(image_base64_gray),
            Bucket.BUCKET,
            f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
        )

      if self.properties.get('file_gcs') is not None:
        self.client_google_cloud.upload_image(
          self._clean_base64(image_base64_rgb),
          f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
        )
        self.client_google_cloud.upload_image(
          self._clean_base64(image_base64_gray),
          f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
        )

      if self.properties.get('file_local') is not None:
        self.client_local_storage.upload_image(
          self._clean_base64(image_base64_rgb),
          f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
        )
        self.client_local_storage.upload_image(
          self._clean_base64(image_base64_gray),
          f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
        )

      self.kariotype_repository.bulk_update(
        self.properties.get('_id', None),
        [
          {
            'id_chromosome': item.get('id_chromosome'),
            'status_centromere': StatusChromosomeEnum.PROCESSED,
            'file_rgb_s3': file_rgb_name if self.properties.get('file_s3') is not None else None,
            'file_gray_s3': file_gray_name if self.properties.get('file_s3') is not None else None,
            'file_rgb_gcs': file_rgb_name if self.properties.get('file_gcs') is not None else None,
            'file_gray_gcs': file_gray_name if self.properties.get('file_gcs') is not None else None,
            'file_rgb_local': file_rgb_name if self.properties.get('file_local') is not None else None,
            'file_gray_local': file_gray_name if self.properties.get('file_local') is not None else None,
            'file_rgb_drive': file_rgb_name if self.properties.get('file_drive') is not None else None,
            'file_gray_drive': file_gray_name if self.properties.get('file_drive') is not None else None,
            'dimension': {
              'x': rotated_image_rgb.shape[1],
              'y': rotated_image_rgb.shape[0]
            },
            'centromere_coord': {
              'x': int(points[1]),
              'y': int(points[0])
            }
          }
        ]
      )

      payload_queue = { 
        'kariotype_id': self.properties.get('_id'),
        'batch': [ item.get('id_chromosome') ]
      }

      self.publish(payload_queue, routing_key="preclassification_queue")
